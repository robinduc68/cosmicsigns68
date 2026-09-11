"""Chart frame builder — the deterministic part of the engine that is ready.

What this module computes today (verified, covered by tests):
    * solar ↔ lunar conversion and the four can–chi pillars
    * the 12 palaces: earthly branch, heavenly stem (ngũ hổ độn), nạp âm
    * cung Mệnh, cung Thân and where Thân resides
    * Cục and the ngũ hành relationship between Mệnh and Cục
    * Tuần không and Triệt lộ

What it deliberately does NOT compute yet: phụ tinh, miếu/vượng/đắc/hãm,
tứ hoá, đại vận and lưu niên. Those arrive with the full engine (see
``docs/astrology-engine.md``). Anything not yet verified is flagged
``provisional`` in the payload so the UI can label it instead of pretending.
"""

from __future__ import annotations

from cosmic_astrology.birth_moment import ResolvedBirthDates, resolve_birth_dates
from cosmic_astrology.calendar.sexagenary import (
    CAN,
    CHI,
    Element,
    hour_branch_index,
    nap_am_element,
    pillars_for_birth,
    sexagenary_index,
)
from cosmic_astrology.chart.types import (
    PALACE_LABELS,
    PALACE_ORDER,
    BirthInput,
    CalendarType,
    Chart,
    EngineStage,
    Gender,
    Palace,
    Star,
    StarKind,
)
from cosmic_astrology.conventions.policies import RuleId, TimezonePolicy
from cosmic_astrology.conventions.profile import ConventionProfile
from cosmic_astrology.conventions.standard import COSMIC_SIGNS_STANDARD_V1
from cosmic_astrology.timezone import resolve_timezone
from cosmic_astrology.trace import TraceLog

__all__ = ["ENGINE_VERSION", "build_chart", "three_directions_four_positions"]

# 0.2.0: fixes mirrored palace names and the Tý/Sửu palace stems. Charts built by
# 0.1.0 may carry wrong palace names, Thân cư, and — when Mệnh is in Tý or Sửu — Cục.
ENGINE_VERSION = "0.2.0-frame"

# Cục số per ngũ hành of cung Mệnh.
_CUC_BY_ELEMENT: dict[Element, tuple[int, str]] = {
    Element.THUY: (2, "Thủy Nhị Cục"),
    Element.MOC: (3, "Mộc Tam Cục"),
    Element.KIM: (4, "Kim Tứ Cục"),
    Element.THO: (5, "Thổ Ngũ Cục"),
    Element.HOA: (6, "Hỏa Lục Cục"),
}

_GENERATES: dict[Element, Element] = {
    Element.MOC: Element.HOA,
    Element.HOA: Element.THO,
    Element.THO: Element.KIM,
    Element.KIM: Element.THUY,
    Element.THUY: Element.MOC,
}

_OVERCOMES: dict[Element, Element] = {
    Element.MOC: Element.THO,
    Element.THO: Element.THUY,
    Element.THUY: Element.HOA,
    Element.HOA: Element.KIM,
    Element.KIM: Element.MOC,
}

_ELEMENT_LABELS: dict[Element, str] = {
    Element.KIM: "Kim",
    Element.MOC: "Mộc",
    Element.THUY: "Thủy",
    Element.HOA: "Hỏa",
    Element.THO: "Thổ",
}

# Triệt lộ không vong, keyed by the can of the birth year.
_TRIET_BY_YEAR_CAN: dict[int, tuple[int, int]] = {
    0: (8, 9),  # Giáp → Thân Dậu
    5: (8, 9),  # Kỷ
    1: (6, 7),  # Ất  → Ngọ Mùi
    6: (6, 7),  # Canh
    2: (4, 5),  # Bính → Thìn Tỵ
    7: (4, 5),  # Tân
    3: (2, 3),  # Đinh → Dần Mão
    8: (2, 3),  # Nhâm
    4: (0, 1),  # Mậu → Tý Sửu
    9: (0, 1),  # Quý
}

# Offsets from cung Tử Vi (counter-clockwise) and cung Thiên Phủ (clockwise).
_TU_VI_CHAIN: tuple[tuple[str, str, int], ...] = (
    ("TU_VI", "Tử Vi", 0),
    ("THIEN_CO", "Thiên Cơ", -1),
    ("THAI_DUONG", "Thái Dương", -3),
    ("VU_KHUC", "Vũ Khúc", -4),
    ("THIEN_DONG", "Thiên Đồng", -5),
    ("LIEM_TRINH", "Liêm Trinh", -8),
)

_THIEN_PHU_CHAIN: tuple[tuple[str, str, int], ...] = (
    ("THIEN_PHU", "Thiên Phủ", 0),
    ("THAI_AM", "Thái Âm", 1),
    ("THAM_LANG", "Tham Lang", 2),
    ("CU_MON", "Cự Môn", 3),
    ("THIEN_TUONG", "Thiên Tướng", 4),
    ("THIEN_LUONG", "Thiên Lương", 5),
    ("THAT_SAT", "Thất Sát", 6),
    ("PHA_QUAN", "Phá Quân", 10),
)


def _element_relation(menh: Element, cuc: Element) -> tuple[str, str]:
    """Relationship between bản mệnh and cục, as ``(code, Vietnamese label)``."""
    if menh is cuc:
        return ("TUONG_HOA", "Mệnh và Cục tương hòa")
    if _GENERATES[cuc] is menh:
        return ("CUC_SINH_MENH", "Cục sinh Mệnh")
    if _GENERATES[menh] is cuc:
        return ("MENH_SINH_CUC", "Mệnh sinh Cục")
    if _OVERCOMES[cuc] is menh:
        return ("CUC_KHAC_MENH", "Cục khắc Mệnh")
    return ("MENH_KHAC_CUC", "Mệnh khắc Cục")


def _tuan_branches(year_can: int, year_chi: int) -> tuple[int, int]:
    """The two branches left empty by the tuần containing the birth year."""
    index = sexagenary_index(year_can, year_chi)
    decade_start_chi = (year_chi - index % 10) % 12
    return ((decade_start_chi + 10) % 12, (decade_start_chi + 11) % 12)


def _tu_vi_branch(cuc_number: int, lunar_day: int) -> int:
    """Position of Tử Vi from cục số and lunar day (counting starts at Dần)."""
    remainder = lunar_day % cuc_number
    padding = 0 if remainder == 0 else cuc_number - remainder
    quotient = (lunar_day + padding) // cuc_number
    branch = (2 + quotient - 1) % 12
    if padding % 2 == 1:
        return (branch - padding) % 12
    return (branch + padding) % 12


def three_directions_four_positions(branch_index: int) -> dict[str, int]:
    """Tam phương tứ chính of a palace: itself, the trine pair and the opposite."""
    return {
        "self": branch_index % 12,
        "trine_left": (branch_index + 4) % 12,
        "trine_right": (branch_index + 8) % 12,
        "opposite": (branch_index + 6) % 12,
    }


def build_chart(
    birth: BirthInput,
    stage: EngineStage = EngineStage.FRAME,
    *,
    profile: ConventionProfile = COSMIC_SIGNS_STANDARD_V1,
    trace: bool = False,
) -> Chart:
    """Build a chart from a birth moment under an explicit convention profile.

    ``stage`` controls how much is placed. ``FRAME`` stops after the verified
    frame; ``PREVIEW`` additionally places the 14 chính tinh, which are marked
    ``provisional`` until the reference test suite covers them.

    ``profile`` decides every school-dependent rule. A birth the profile has no
    rule for — a 23:xx birth while the late-Zi question is open — raises
    :class:`UnresolvedConventionError` instead of being guessed at.
    """
    if stage is EngineStage.FULL:
        raise NotImplementedError("Engine đầy đủ chưa được triển khai (xem docs/roadmap.md)")

    log = TraceLog.for_profile(profile) if trace else None

    tz = resolve_timezone(
        policy=TimezonePolicy(profile.policy(RuleId.TIMEZONE)),
        year=birth.year,
        month=birth.month,
        day=birth.day,
        hour=birth.hour,
        minute=birth.minute,
        timezone_id=birth.timezone_id,
        fallback_offset=birth.tz_offset,
    )
    tz_offset = tz.utc_offset_hours

    dates: ResolvedBirthDates = resolve_birth_dates(
        profile=profile,
        calendar_is_lunar=birth.calendar_type is CalendarType.LUNAR,
        day=birth.day,
        month=birth.month,
        year=birth.year,
        hour=birth.hour,
        is_leap_month=birth.is_leap_month,
        tz_offset=tz_offset,
    )
    lunar = dates.lunar
    solar_day, solar_month, solar_year = dates.placement_solar

    if log is not None:
        log.record(profile, RuleId.TIMEZONE, f"UTC{tz_offset:+g}",
                   timezone_id=birth.timezone_id, source=tz.source)
        log.record(profile, RuleId.LATE_ZI,
                   f"ngày an sao {dates.placement_solar}, trụ ngày {dates.day_pillar_solar}",
                   hour=birth.hour, late_zi=dates.late_zi)

    pillars = pillars_for_birth(
        solar_day,
        solar_month,
        solar_year,
        birth.hour,
        lunar,
        tz_offset,
        day_pillar_solar=dates.day_pillar_solar,
    )
    hour_chi = hour_branch_index(birth.hour)

    # An Mệnh: from cung Dần, count forward to the lunar month, then back to the
    # birth hour. An Thân: same start, but both counts move forward.
    menh_branch = (2 + (lunar.month - 1) - hour_chi) % 12
    than_branch = (2 + (lunar.month - 1) + hour_chi) % 12

    # Ngũ hổ độn: the stem of cung Dần is fixed by the stem of the birth year.
    dan_stem = (pillars.year.can_index * 2 + 2) % 10

    tuan = _tuan_branches(pillars.year.can_index, pillars.year.chi_index)
    triet = _TRIET_BY_YEAR_CAN[pillars.year.can_index]

    palaces: list[Palace] = []
    for offset, palace_name in enumerate(PALACE_ORDER):
        # PALACE_ORDER lists Mệnh, Phụ Mẫu, Phúc Đức, … Huynh Đệ, which runs clockwise
        # (thuận). The classical listing Mệnh → Huynh Đệ → Phu Thê … is the same
        # arrangement read counter-clockwise. Walking this list counter-clockwise, as
        # the loop once did, mirrored ten of the twelve palace names.
        branch = (menh_branch + offset) % 12
        # Ngũ hổ độn runs *forward* from Dần through the lunar year, so Tý and Sửu are
        # months 11 and 12 (Dần + 10, Dần + 11), not Dần − 2 and Dần − 1. The two only
        # differ modulo 10, which is how the error hid — and it changed Cục whenever
        # Mệnh sat in Tý or Sửu.
        stem = (dan_stem + ((branch - 2) % 12)) % 10
        nap_am_name, element = nap_am_element(stem, branch)
        palaces.append(
            Palace(
                name=palace_name,
                label=PALACE_LABELS[palace_name],
                branch_index=branch,
                branch=CHI[branch],
                stem=CAN[stem],
                stem_index=stem,
                element=element,
                nap_am=nap_am_name,
                is_menh=branch == menh_branch,
                is_than=branch == than_branch,
                has_tuan=branch in tuan,
                has_triet=branch in triet,
            )
        )

    by_branch = {p.branch_index: p for p in palaces}
    menh_palace = by_branch[menh_branch]
    than_palace = by_branch[than_branch]

    cuc_number, cuc_label = _CUC_BY_ELEMENT[menh_palace.element]
    menh_element = nap_am_element(pillars.year.can_index, pillars.year.chi_index)[1]
    relation_code, relation_label = _element_relation(menh_element, menh_palace.element)

    if log is not None:
        log.record(profile, RuleId.MENH_PLACEMENT, CHI[menh_branch],
                   lunar_month=lunar.month, hour_branch=CHI[hour_chi])
        log.record(profile, RuleId.THAN_PLACEMENT, CHI[than_branch],
                   lunar_month=lunar.month, hour_branch=CHI[hour_chi])
        log.record(profile, RuleId.CUC, cuc_label,
                   menh_palace=CHI[menh_branch], nap_am=menh_palace.nap_am)

    if stage is EngineStage.PREVIEW:
        _place_major_stars(by_branch, cuc_number, lunar.day, profile=profile, log=log)

    is_yang_year = pillars.year.is_yang
    is_male = birth.gender is Gender.MALE
    yin_yang_label = ("Dương" if is_yang_year else "Âm") + (" Nam" if is_male else " Nữ")

    return Chart(
        engine_stage=stage,
        engine_version=ENGINE_VERSION,
        convention_profile=profile.profile_id,
        convention_version=profile.version,
        convention_rules=[profile.binding(r).to_dict() for r in RuleId],
        timezone=tz.to_dict(),
        date_resolution=dates.to_dict(),
        trace=log.to_dict() if log is not None else None,
        birth={
            "name": birth.name,
            "gender": birth.gender.value,
            "calendar_type": birth.calendar_type.value,
            "solar": {
                "day": solar_day,
                "month": solar_month,
                "year": solar_year,
                "hour": birth.hour,
                "minute": birth.minute,
            },
            "birth_place": birth.birth_place,
            "tz_offset": tz_offset,
            "hour_branch": CHI[hour_chi],
            "hour_branch_index": hour_chi,
        },
        lunar_birth={
            "day": lunar.day,
            "month": lunar.month,
            "year": lunar.year,
            "is_leap_month": lunar.is_leap_month,
            "year_pillar": pillars.year.name,
        },
        pillars=pillars.to_dict(),
        yin_yang={
            "year_is_yang": is_yang_year,
            "gender_is_male": is_male,
            "label": yin_yang_label,
            "is_thuan_ly": is_yang_year == is_male,
        },
        menh={
            "branch": CHI[menh_branch],
            "branch_index": menh_branch,
            "element": menh_element.value,
            "element_label": _ELEMENT_LABELS[menh_element],
            "nap_am": nap_am_element(pillars.year.can_index, pillars.year.chi_index)[0],
            "three_directions_four_positions": three_directions_four_positions(menh_branch),
        },
        than={
            "branch": CHI[than_branch],
            "branch_index": than_branch,
            "resides_in": than_palace.name.value,
            "resides_in_label": than_palace.label,
        },
        cuc={
            "number": cuc_number,
            "element": menh_palace.element.value,
            "element_label": _ELEMENT_LABELS[menh_palace.element],
            "label": cuc_label,
            "relation": relation_code,
            "relation_label": relation_label,
        },
        palaces=palaces,
    )


def _place_major_stars(
    by_branch: dict[int, Palace],
    cuc_number: int,
    lunar_day: int,
    *,
    profile: ConventionProfile,
    log: TraceLog | None = None,
) -> None:
    """Place the 14 chính tinh (PREVIEW stage only, not yet reference-tested)."""
    tu_vi = _tu_vi_branch(cuc_number, lunar_day)
    thien_phu = (4 - tu_vi) % 12
    if log is not None:
        log.record(profile, RuleId.TU_VI_PLACEMENT, CHI[tu_vi],
                   cuc=cuc_number, lunar_day=lunar_day)
    for code, label, offset in _TU_VI_CHAIN:
        branch = (tu_vi + offset) % 12
        by_branch[branch].stars.append(
            Star(code=code, label=label, kind=StarKind.MAJOR, provisional=True)
        )
        if log is not None:
            log.record(profile, RuleId.MAJOR_STARS, f"{label} → {CHI[branch]}",
                       chain="Tử Vi", anchor=CHI[tu_vi], offset=offset)
    for code, label, offset in _THIEN_PHU_CHAIN:
        branch = (thien_phu + offset) % 12
        by_branch[branch].stars.append(
            Star(code=code, label=label, kind=StarKind.MAJOR, provisional=True)
        )
        if log is not None:
            log.record(profile, RuleId.MAJOR_STARS, f"{label} → {CHI[branch]}",
                       chain="Thiên Phủ", anchor=CHI[thien_phu], offset=offset)
