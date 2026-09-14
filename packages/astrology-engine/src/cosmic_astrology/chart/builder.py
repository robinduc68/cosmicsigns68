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

import logging
from collections.abc import Callable
from datetime import UTC, datetime

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
from cosmic_astrology.chart.model import (
    BirthInformation,
    PalaceCycles,
    StarCategory,
    StarProvenance,
    VoidMark,
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
)
from cosmic_astrology.conventions.nam_phai import COSMIC_SIGNS_NAM_PHAI_V1
from cosmic_astrology.conventions.policies import (
    MajorCycleStartAgePolicy,
    RuleId,
    TimezonePolicy,
)
from cosmic_astrology.conventions.profile import (
    ConventionProfile,
    UnresolvedConventionError,
    validate_convention_profile,
)
from cosmic_astrology.cycles import major_cycle, trang_sinh
from cosmic_astrology.stars import four_transformations, placement
from cosmic_astrology.stars.catalog import definition_for
from cosmic_astrology.timezone import resolve_timezone
from cosmic_astrology.trace import TraceLog

__all__ = ["ENGINE_VERSION", "build_chart", "three_directions_four_positions"]

#: Library-style logger: the engine reports, the host application decides what to
#: do about it. A missing catalogue entry must never take a chart down.
_logger = logging.getLogger(__name__)

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
#
# Star **ids** only: the name, ngũ hành, âm/dương and category of each star live in
# ``stars.catalog`` and are looked up from there. A placement rule that also carried
# display names would be two sources of truth for the same star.
_TU_VI_CHAIN: tuple[tuple[str, int], ...] = (
    ("TU_VI", 0),
    ("THIEN_CO", -1),
    ("THAI_DUONG", -3),
    ("VU_KHUC", -4),
    ("THIEN_DONG", -5),
    ("LIEM_TRINH", -8),
)

_THIEN_PHU_CHAIN: tuple[tuple[str, int], ...] = (
    ("THIEN_PHU", 0),
    ("THAI_AM", 1),
    ("THAM_LANG", 2),
    ("CU_MON", 3),
    ("THIEN_TUONG", 4),
    ("THIEN_LUONG", 5),
    ("THAT_SAT", 6),
    ("PHA_QUAN", 10),
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
    profile: ConventionProfile = COSMIC_SIGNS_NAM_PHAI_V1,
    trace: bool = False,
    generated_at: str | None = None,
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

    # Injectable so a fixture can pin it; a chart that restamped itself on every
    # run would make byte-for-byte fixture comparison impossible.
    generated_at = generated_at or datetime.now(UTC).isoformat(timespec="seconds")
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
                # Same predicate as before; the mark now carries which rule put it
                # there so a reviewer does not have to read the code to find out.
                tuan=VoidMark(
                    present=branch in tuan,
                    verification=profile.binding(RuleId.TUAN).verification,
                    source_rule=f"tuan/{profile.binding(RuleId.TUAN).policy}",
                ),
                triet=VoidMark(
                    present=branch in triet,
                    verification=profile.binding(RuleId.TRIET).verification,
                    source_rule=f"triet/{profile.binding(RuleId.TRIET).policy}",
                ),
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
        _place_major_stars(by_branch, cuc_number, lunar.day, profile=profile, trace_log=log)
        _place_supporting_stars(
            by_branch,
            year_stem=pillars.year.can_index,
            year_branch=pillars.year.chi_index,
            lunar_month=lunar.month,
            hour_branch=hour_chi,
            profile=profile,
            trace_log=log,
        )
        # Sau cùng: Tứ Hóa gắn vào sao đã an, nên phải chạy sau cả chính tinh lẫn phụ tinh.
        _apply_four_transformations(
            by_branch, year_stem=pillars.year.can_index, profile=profile, trace_log=log
        )

    _attach_cycles(
        by_branch,
        menh_branch=menh_branch,
        cuc_number=cuc_number,
        cuc_element=menh_palace.element,
        year_is_yang=pillars.year.is_yang,
        is_male=birth.gender is Gender.MALE,
        profile=profile,
        trace_log=log,
    )

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
        generated_at=generated_at,
        production_ready=validate_convention_profile(profile).production_ready,
        birth=BirthInformation(
            full_name=birth.name,
            gender=birth.gender.value,
            calendar_type=birth.calendar_type.value,
            solar_day=solar_day,
            solar_month=solar_month,
            solar_year=solar_year,
            hour=birth.hour,
            minute=birth.minute,
            hour_branch=CHI[hour_chi],
            hour_branch_index=hour_chi,
            historical_utc_offset=tz_offset,
            timezone_id=birth.timezone_id,
            birth_place=birth.birth_place,
        ),
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


def _placed_star(
    star_id: str,
    branch: str,
    *,
    profile: ConventionProfile,
    rule: RuleId = RuleId.MAJOR_STARS,
) -> Star:
    """A placed star, with its catalogue entry attached.

    Everything about *what* the star is comes from the catalogue; this function
    only knows *where* it landed. A star the catalogue has never heard of still
    gets placed — losing a placement over missing display metadata would be worse
    than rendering it plainly — but it is logged, and it carries no invented
    element. ``strength`` stays ``None``: the miếu/vượng table is not implemented.
    """
    definition = definition_for(star_id)
    if definition is None:
        # A programming error, not a user's problem: a placement rule has named a
        # star nobody catalogued. Tests fail on it; production carries on.
        _logger.warning(
            "Sao %r được an nhưng chưa có trong catalog — vẽ bằng tên id và không có "
            "ngũ hành. Thêm mục vào cosmic_astrology/stars/catalog.py.",
            star_id,
        )
    binding = profile.binding(rule)
    return Star(
        id=star_id,
        name=definition.vietnamese_name if definition else star_id,
        category=definition.category if definition else StarCategory.OTHER,
        element=definition.element if definition else None,
        polarity=definition.polarity if definition else None,
        palace_branch=branch,
        provenance=StarProvenance(
            rule=f"{rule.value}/{binding.policy}",
            verification=binding.verification,
            blocked_by=binding.blocked_by,
            note=binding.note,
        ),
    )


#: Nhóm phụ tinh 1. Mỗi mục: (mã sao, mã quy ước, tên đầu vào, hàm an sao).
#: Bảng này là chỗ duy nhất nối "sao nào" với "luật nào" — thêm một sao là thêm một
#: dòng, không phải sửa vòng lặp.
_SUPPORTING_GROUP_1: tuple[tuple[str, RuleId, str, Callable[[int], int]], ...] = (
    ("VAN_XUONG", RuleId.VAN_XUONG_VAN_KHUC, "hour_branch", placement.place_van_xuong),
    ("VAN_KHUC", RuleId.VAN_XUONG_VAN_KHUC, "hour_branch", placement.place_van_khuc),
    ("TA_PHU", RuleId.TA_PHU_HUU_BAT, "lunar_month", placement.place_ta_phu),
    ("HUU_BAT", RuleId.TA_PHU_HUU_BAT, "lunar_month", placement.place_huu_bat),
    ("THIEN_KHOI", RuleId.THIEN_KHOI_THIEN_VIET, "year_stem", placement.place_thien_khoi),
    ("THIEN_VIET", RuleId.THIEN_KHOI_THIEN_VIET, "year_stem", placement.place_thien_viet),
    ("LOC_TON", RuleId.LOC_TON, "year_stem", placement.place_loc_ton),
    ("DAO_HOA", RuleId.DAO_HOA, "year_branch", placement.place_dao_hoa),
    ("HONG_LOAN", RuleId.HONG_LOAN_THIEN_HY, "year_branch", placement.place_hong_loan),
    ("THIEN_HY", RuleId.HONG_LOAN_THIEN_HY, "year_branch", placement.place_thien_hy),
    ("THIEN_MA", RuleId.THIEN_MA, "year_branch", placement.place_thien_ma),
)


def _place_supporting_stars(
    by_branch: dict[int, Palace],
    *,
    year_stem: int,
    year_branch: int,
    lunar_month: int,
    hour_branch: int,
    profile: ConventionProfile,
    trace_log: TraceLog | None = None,
) -> None:
    """Place phụ tinh nhóm 1.

    A profile that has not named a school leaves these rules unresolved; asking it
    for one raises rather than guessing, so a chart built under the plain standard
    profile simply carries no phụ tinh instead of carrying somebody's guess.

    Kình Dương and Đà La are placed after the loop because they are positioned
    relative to Lộc Tồn rather than from the birth data directly.
    """
    inputs = {
        "year_stem": year_stem,
        "year_branch": year_branch,
        "lunar_month": lunar_month,
        "hour_branch": hour_branch,
    }
    if profile.binding(RuleId.VAN_XUONG_VAN_KHUC).is_unresolved:
        return

    placed: list[tuple[str, RuleId, int]] = [
        (star_id, rule, place(inputs[argument]))
        for star_id, rule, argument, place in _SUPPORTING_GROUP_1
    ]

    loc_ton_binding = profile.binding(RuleId.KINH_DUONG_DA_LA)
    if not loc_ton_binding.is_unresolved:
        loc_ton = placement.place_loc_ton(year_stem)
        placed.append(("KINH_DUONG", RuleId.KINH_DUONG_DA_LA, placement.place_kinh_duong(loc_ton)))
        placed.append(("DA_LA", RuleId.KINH_DUONG_DA_LA, placement.place_da_la(loc_ton)))

    for star_id, rule, branch in placed:
        star = _placed_star(star_id, CHI[branch], profile=profile, rule=rule)
        by_branch[branch].stars.append(star)
        if trace_log is not None:
            trace_log.record(profile, rule, f"{star.name} → {CHI[branch]}", **inputs)


def _apply_four_transformations(
    by_branch: dict[int, Palace],
    *,
    year_stem: int,
    profile: ConventionProfile,
    trace_log: TraceLog | None = None,
) -> None:
    """Attach Tứ Hóa to stars that are already placed.

    No star is created here. Tứ Hóa is a *state* a placed star carries, so adding a
    fifth star per chart would make every star count depend on the birth year.

    A target the engine does not place yet is reported rather than dropped: the
    chart stays usable, but the gap is visible instead of looking like the birth
    year simply has no hóa there.
    """
    binding = profile.binding(RuleId.FOUR_TRANSFORMATIONS)
    if binding.is_unresolved:
        return

    table = four_transformations.transformations_for_stem(year_stem)
    placed: dict[str, tuple[int, int]] = {
        star.id: (branch, index)
        for branch, palace in by_branch.items()
        for index, star in enumerate(palace.stars)
    }

    for transformation, star_id in table.items():
        target = placed.get(star_id)
        if target is None:
            definition = definition_for(star_id)
            name = definition.vietnamese_name if definition else star_id
            _logger.warning(
                "Thiếu sao đích của Tứ Hóa: %s (%s) — engine chưa an sao này, nên "
                "%s của can %s không gắn được vào đâu.",
                name,
                star_id,
                transformation.value,
                CAN[year_stem],
            )
            if trace_log is not None:
                trace_log.record(
                    profile,
                    RuleId.FOUR_TRANSFORMATIONS,
                    f"{transformation.short_label}: CHƯA GIẢI ĐƯỢC — thiếu sao {name}",
                    can_nam=CAN[year_stem],
                    sao_dich=star_id,
                )
            continue

        branch, index = target
        palace = by_branch[branch]
        star = palace.stars[index].with_transformation(transformation)
        palace.stars[index] = star
        if trace_log is not None:
            trace_log.record(
                profile,
                RuleId.FOUR_TRANSFORMATIONS,
                f"{star.name} hóa {transformation.short_label} tại {CHI[branch]}",
                can_nam=CAN[year_stem],
                bang=four_transformations.TABLE_VERSION,
                sao_dich=star_id,
            )


def _attach_cycles(
    by_branch: dict[int, Palace],
    *,
    menh_branch: int,
    cuc_number: int,
    cuc_element: Element,
    year_is_yang: bool,
    is_male: bool,
    profile: ConventionProfile,
    trace_log: TraceLog | None = None,
) -> None:
    """Lay vòng Tràng Sinh and đại vận onto the twelve palaces.

    Both are laid on **branches**, not on palace names. The twelve palace names are
    fixed by ``PALACE_ORDER`` and never reverse; only the đại vận walk has a
    direction. Keeping the two apart is what this function is careful about.
    """
    trang_sinh_start = profile.binding(RuleId.TRANG_SINH_START)
    trang_sinh_dir = profile.binding(RuleId.TRANG_SINH_DIRECTION)
    cycle_dir = profile.binding(RuleId.MAJOR_CYCLE_DIRECTION)
    start_age = profile.binding(RuleId.MAJOR_CYCLE_START_AGE)

    # Cục số is odd for Thủy/Mộc/Hỏa cục (2, 3, 6 → …) — the polarity used by the
    # alternative direction policy. Computed here so the policy module stays free
    # of chart concepts.
    cuc_is_yang = cuc_number % 2 == 0

    start = trang_sinh.start_branch(cuc_element, policy=trang_sinh_start.policy)
    forward_ts = trang_sinh.runs_forward(
        year_is_yang=year_is_yang,
        is_male=is_male,
        cuc_is_yang=cuc_is_yang,
        policy=trang_sinh_dir.policy,
    )
    stages = trang_sinh.stage_by_branch(start, forward=forward_ts)

    forward_dv = major_cycle.runs_forward(
        year_is_yang=year_is_yang, is_male=is_male, policy=cycle_dir.policy
    )
    if start_age.policy != MajorCycleStartAgePolicy.CUC_NUMBER.value:
        raise UnresolvedConventionError(
            "Chưa chốt tuổi khởi đại vận, nên không dựng được dãy đại vận."
        )
    cycles = major_cycle.major_cycles(
        menh_branch=menh_branch, cuc_number=cuc_number, forward=forward_dv
    )
    direction_label = "FORWARD" if forward_dv else "BACKWARD"

    for cycle in cycles:
        palace = by_branch[cycle.branch_index]
        palace.cycles = PalaceCycles(
            major_cycle_age_start=cycle.age_start,
            major_cycle_age_end=cycle.age_end,
            major_cycle_index=cycle.index,
            major_cycle_direction=direction_label,
            trang_sinh_stage=stages[cycle.branch_index],
        )

    if trace_log is None:
        return
    polarity = "dương" if year_is_yang else "âm"
    gender = "nam" if is_male else "nữ"
    trace_log.record(
        profile,
        RuleId.TRANG_SINH_START,
        f"Tràng Sinh tại {CHI[start]}",
        cuc=f"{cuc_element.value} {cuc_number}",
        bang="ngũ hành cục → địa chi khởi",
    )
    trace_log.record(
        profile,
        RuleId.TRANG_SINH_DIRECTION,
        "thuận" if forward_ts else "nghịch",
        nam_sinh=polarity,
        gioi_tinh=gender,
        cuc_am_duong="dương" if cuc_is_yang else "âm",
        # Spelled out so "why is this palace Đế Vượng?" is answered by reading the
        # trace, rather than by re-deriving the walk from the start and direction.
        chuoi=" → ".join(
            f"{CHI[(start + (1 if forward_ts else -1) * i) % 12]}:{stage}"
            for i, stage in enumerate(trang_sinh.TRANG_SINH_STAGES)
        ),
    )
    trace_log.record(
        profile,
        RuleId.MAJOR_CYCLE_DIRECTION,
        "thuận" if forward_dv else "nghịch",
        nam_sinh=polarity,
        gioi_tinh=gender,
        luu_y="tên 12 cung không đảo theo chiều này",
    )
    trace_log.record(
        profile,
        RuleId.MAJOR_CYCLE_START_AGE,
        f"đại vận 1: {cycles[0].age_start}–{cycles[0].age_end} tuổi tại {CHI[menh_branch]}",
        cuc_so=cuc_number,
        moi_cung=f"{major_cycle.PALACE_SPAN_YEARS} năm",
    )


def _place_major_stars(
    by_branch: dict[int, Palace],
    cuc_number: int,
    lunar_day: int,
    *,
    profile: ConventionProfile,
    trace_log: TraceLog | None = None,
) -> None:
    """Place the 14 chính tinh (PREVIEW stage only, not yet reference-tested)."""
    tu_vi = _tu_vi_branch(cuc_number, lunar_day)
    thien_phu = (4 - tu_vi) % 12
    if trace_log is not None:
        trace_log.record(profile, RuleId.TU_VI_PLACEMENT, CHI[tu_vi],
                         cuc=cuc_number, lunar_day=lunar_day)
    for star_id, offset in _TU_VI_CHAIN:
        branch = (tu_vi + offset) % 12
        star = _placed_star(star_id, CHI[branch], profile=profile)
        by_branch[branch].stars.append(star)
        if trace_log is not None:
            trace_log.record(profile, RuleId.MAJOR_STARS, f"{star.name} → {CHI[branch]}",
                             chain="Tử Vi", anchor=CHI[tu_vi], offset=offset)
    for star_id, offset in _THIEN_PHU_CHAIN:
        branch = (thien_phu + offset) % 12
        star = _placed_star(star_id, CHI[branch], profile=profile)
        by_branch[branch].stars.append(star)
        if trace_log is not None:
            trace_log.record(profile, RuleId.MAJOR_STARS, f"{star.name} → {CHI[branch]}",
                             chain="Thiên Phủ", anchor=CHI[thien_phu], offset=offset)
