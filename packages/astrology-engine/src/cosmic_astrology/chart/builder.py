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
from dataclasses import replace
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
    TraditionalMetadata,
    VoidMark,
    rule_fingerprint,
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
    PalaceName,
    Star,
    StarStrength,
    Transformation,
)
from cosmic_astrology.conventions.nam_phai import COSMIC_SIGNS_NAM_PHAI_V1
from cosmic_astrology.conventions.policies import (
    MajorCycleStartAgePolicy,
    RuleId,
    TimezonePolicy,
    VerificationStatus,
)
from cosmic_astrology.conventions.profile import (
    ConventionProfile,
    UnresolvedConventionError,
    validate_convention_profile,
)
from cosmic_astrology.cycles import major_cycle, trang_sinh
from cosmic_astrology.stars import four_transformations, placement, reference, strength
from cosmic_astrology.stars import placement_group2 as group2
from cosmic_astrology.stars import placement_group3 as group3
from cosmic_astrology.stars import placement_malefic as malefic
from cosmic_astrology.stars.catalog import STAR_CATALOG, definition_for
from cosmic_astrology.stars.rulers import rulers_for_year_branch
from cosmic_astrology.timezone import resolve_timezone
from cosmic_astrology.trace import TraceLog

__all__ = ["ENGINE_VERSION", "build_chart", "three_directions_four_positions"]

#: Library-style logger: the engine reports, the host application decides what to
#: do about it. A missing catalogue entry must never take a chart down.
_logger = logging.getLogger(__name__)

# 0.2.0: fixes mirrored palace names and the Tý/Sửu palace stems. Charts built by
# 0.1.0 may carry wrong palace names, Thân cư, and — when Mệnh is in Tý or Sửu — Cục.
#
# 0.3.0: the star set grew from 14 to 88 — star catalogue, Tràng Sinh, đại vận, Tứ
# Hóa, three supporting groups and the malefic group. This string stayed at 0.2.0
# through all of it, so charts stored along the way reported themselves as current
# while missing up to 61 stars. That is why ``Chart.rule_fingerprint`` now exists:
# a version string only works if somebody remembers it, and nobody did.
#
# 0.3.1: Thiên Quý now counts backward from Văn Khúc instead of forward. Only that
# one star moves; the star set is unchanged, so this is exactly the kind of change
# the fingerprint alone would miss if the rule policy had not also been renamed.
#
# 0.4.0: gỡ chặn bốn sao (Giải Thần, Thiên Trù, Thiên Y, Lưu Hà) và thêm hai nhãn
# Chủ Mệnh / Chủ Thân. Tập sao đi từ 88 lên 92, nên lần này vân tay tự đổi — nhưng
# phiên bản vẫn phải nâng, vì nó nói *chủ ý*, còn vân tay chỉ nói *thực tế*.
#
# 0.4.1: Giải Thần đổi sang biến thể tam hợp chi năm, và hàng Kỷ của bảng Thiên Trù
# đổi theo lá số đối chiếu. Hai sao dịch chỗ, không sao nào khác đụng tới.
#
# 0.4.2: độ sáng nay đọc từ 23 ô đã quan sát được trên lá số đối chiếu, chỗ nào bảng
# trường phái chưa có. Không sao nào dịch chỗ — chỉ thêm metadata.
#
# 0.4.3: mỗi ngôi sao nay mang thêm ``transformation_strengths`` — độ sáng của từng
# Tứ Hóa nó đang giữ. Thêm trường, không dịch sao nào.
ENGINE_VERSION = "0.4.3-frame"


def current_rule_fingerprint(profile: ConventionProfile = COSMIC_SIGNS_NAM_PHAI_V1) -> str:
    """Vân tay của engine *hiện hành* dưới một hồ sơ quy ước.

    Dùng ``STAR_CATALOG`` chứ không dùng một lá số cụ thể, nên gọi được mà không
    phải tính lại lá số — bộ kiểm tra lạc hậu chạy trên mỗi lần đọc. Hai giá trị
    này khớp nhau vì mọi lá số đều an đủ tập sao trong catalog; điều đó được khoá
    bằng test, không phải bằng niềm tin.
    """
    return rule_fingerprint(
        STAR_CATALOG.keys(),
        (
            (rule.value, binding.policy)
            for rule in RuleId
            if (binding := profile.binding(rule)).implemented
        ),
    )


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
        log.record(
            profile,
            RuleId.TIMEZONE,
            f"UTC{tz_offset:+g}",
            timezone_id=birth.timezone_id,
            source=tz.source,
        )
        log.record(
            profile,
            RuleId.LATE_ZI,
            f"ngày an sao {dates.placement_solar}, trụ ngày {dates.day_pillar_solar}",
            hour=birth.hour,
            late_zi=dates.late_zi,
        )

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
        log.record(
            profile,
            RuleId.MENH_PLACEMENT,
            CHI[menh_branch],
            lunar_month=lunar.month,
            hour_branch=CHI[hour_chi],
        )
        log.record(
            profile,
            RuleId.THAN_PLACEMENT,
            CHI[than_branch],
            lunar_month=lunar.month,
            hour_branch=CHI[hour_chi],
        )
        log.record(
            profile, RuleId.CUC, cuc_label, menh_palace=CHI[menh_branch], nap_am=menh_palace.nap_am
        )

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
        _place_supporting_stars_group_2(
            by_branch,
            year_stem=pillars.year.can_index,
            year_branch=pillars.year.chi_index,
            lunar_month=lunar.month,
            lunar_day=lunar.day,
            hour_branch=hour_chi,
            menh_branch=menh_branch,
            than_branch=than_branch,
            # Cùng luật chiều với đại vận: dương nam / âm nữ đi thuận.
            cycle_forward=pillars.year.is_yang == (birth.gender is Gender.MALE),
            profile=profile,
            trace_log=log,
        )
        _place_star_cycles(
            by_branch,
            year_branch=pillars.year.chi_index,
            cycle_forward=pillars.year.is_yang == (birth.gender is Gender.MALE),
            profile=profile,
            trace_log=log,
        )
        _place_group_3_stars(
            by_branch,
            year_stem=pillars.year.can_index,
            year_branch=pillars.year.chi_index,
            lunar_month=lunar.month,
            hour_branch=hour_chi,
            profile=profile,
            trace_log=log,
        )
        _place_malefic_stars(
            by_branch,
            year_branch=pillars.year.chi_index,
            hour_branch=hour_chi,
            cycle_forward=pillars.year.is_yang == (birth.gender is Gender.MALE),
            profile=profile,
            trace_log=log,
        )
        # Sau cùng: Tứ Hóa gắn vào sao đã an, nên phải chạy sau cả chính tinh lẫn phụ tinh.
        _apply_four_transformations(
            by_branch, year_stem=pillars.year.can_index, profile=profile, trace_log=log
        )
        _apply_star_strength(by_branch, profile=profile)

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

    # Chủ Mệnh / Chủ Thân là hai **nhãn**, không phải sao an vào cung. Chúng đi vào
    # ``traditional`` chứ không vào ``palace.stars``: thêm chúng vào danh sách sao sẽ
    # làm mọi phép đếm sai và khiến lá số hiện hai lần cùng một ngôi sao.
    if profile.binding(RuleId.CHU_MENH_CHU_THAN).is_unresolved:
        chu_menh, chu_than = None, None
    else:
        chu_menh, chu_than = rulers_for_year_branch(pillars.year.chi_index)

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
        traditional=TraditionalMetadata(chu_menh=chu_menh, chu_than=chu_than),
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


#: Nhóm phụ tinh 2. Sáu sao đầu chỉ cần chi năm; sáu sao sau phụ thuộc vị trí sao
#: hoặc cung đã an, nên nhóm này **bắt buộc chạy sau nhóm 1**.
_GROUP_2_FROM_YEAR_BRANCH: tuple[tuple[str, RuleId, Callable[[int], int]], ...] = (
    ("LONG_TRI", RuleId.LONG_TRI_PHUONG_CAC, group2.place_long_tri),
    ("PHUONG_CAC", RuleId.LONG_TRI_PHUONG_CAC, group2.place_phuong_cac),
    ("THIEN_DUC", RuleId.THIEN_DUC_NGUYET_DUC, group2.place_thien_duc),
    ("NGUYET_DUC", RuleId.THIEN_DUC_NGUYET_DUC, group2.place_nguyet_duc),
    ("HOA_CAI", RuleId.HOA_CAI, group2.place_hoa_cai),
)


def _place_supporting_stars_group_2(
    by_branch: dict[int, Palace],
    *,
    year_stem: int,
    year_branch: int,
    lunar_month: int,
    lunar_day: int,
    hour_branch: int,
    menh_branch: int,
    than_branch: int,
    cycle_forward: bool,
    profile: ConventionProfile,
    trace_log: TraceLog | None = None,
) -> None:
    """Place phụ tinh nhóm 2.

    Six of these are positioned relative to a star that group 1 already placed
    (Tả Phù, Hữu Bật, Văn Xương, Văn Khúc) or to cung Mệnh / cung Thân. Those
    anchors are read back off the chart rather than recomputed, so there is only
    one place that decides where Tả Phù sits.

    A profile that has not named a school leaves these rules unresolved and the
    chart simply carries no group-2 stars.
    """
    if profile.binding(RuleId.LONG_TRI_PHUONG_CAC).is_unresolved:
        return

    anchors = {star.id: branch for branch, palace in by_branch.items() for star in palace.stars}
    placed: list[tuple[str, RuleId, int, dict[str, object]]] = []

    for star_id, rule, place in _GROUP_2_FROM_YEAR_BRANCH:
        year_inputs: dict[str, object] = {"chi_nam": CHI[year_branch]}
        placed.append((star_id, rule, place(year_branch), year_inputs))

    #: ``(mã sao, luật, mã sao neo, hàm)`` — sao neo do nhóm 1 an.
    anchored: tuple[tuple[str, RuleId, str, Callable[[int, int], int]], ...] = (
        ("TAM_THAI", RuleId.TAM_THAI_BAT_TOA, "TA_PHU", group2.place_tam_thai),
        ("BAT_TOA", RuleId.TAM_THAI_BAT_TOA, "HUU_BAT", group2.place_bat_toa),
        ("AN_QUANG", RuleId.AN_QUANG_THIEN_QUY, "VAN_XUONG", group2.place_an_quang),
        ("THIEN_QUY", RuleId.AN_QUANG_THIEN_QUY, "VAN_KHUC", group2.place_thien_quy),
    )
    for star_id, rule, anchor_id, place_from_anchor in anchored:
        anchor_branch = anchors.get(anchor_id)
        if anchor_branch is None:
            # Nhóm 1 chưa an sao neo — không đoán một vị trí thay thế.
            _logger.warning("Thiếu sao neo %s nên không an được %s.", anchor_id, star_id)
            continue
        placed.append(
            (
                star_id,
                rule,
                place_from_anchor(anchor_branch, lunar_day),
                {"sao_neo": f"{anchor_id}@{CHI[anchor_branch]}", "ngay_am": lunar_day},
            )
        )

    placed.append(
        (
            "THIEN_TAI",
            RuleId.THIEN_TAI_THIEN_THO,
            group2.place_thien_tai(menh_branch, year_branch),
            {"cung_menh": CHI[menh_branch], "chi_nam": CHI[year_branch]},
        )
    )
    placed.append(
        (
            "THIEN_THO",
            RuleId.THIEN_TAI_THIEN_THO,
            group2.place_thien_tho(than_branch, year_branch),
            {"cung_than": CHI[than_branch], "chi_nam": CHI[year_branch]},
        )
    )

    stem_inputs: dict[str, object] = {"can_nam": CAN[year_stem]}
    quy_nhan = RuleId.THIEN_QUAN_THIEN_PHUC
    placed.append(("THIEN_QUAN", quy_nhan, group2.place_thien_quan(year_stem), stem_inputs))
    placed.append(("THIEN_PHUC", quy_nhan, group2.place_thien_phuc(year_stem), stem_inputs))

    month_inputs: dict[str, object] = {"thang_am": lunar_month}
    giai = RuleId.THIEN_GIAI_DIA_GIAI
    placed.append(("THIEN_GIAI", giai, group2.place_thien_giai(lunar_month), month_inputs))
    placed.append(("DIA_GIAI", giai, group2.place_dia_giai(lunar_month), month_inputs))

    hour_inputs: dict[str, object] = {"gio_sinh": CHI[hour_branch]}
    thai_phu = RuleId.THAI_PHU_PHONG_CAO
    placed.append(("THAI_PHU", thai_phu, group2.place_thai_phu(hour_branch), hour_inputs))
    placed.append(("PHONG_CAO", thai_phu, group2.place_phong_cao(hour_branch), hour_inputs))

    # Quốc Ấn, Đường Phù và Hỷ Thần đều neo vào Lộc Tồn — đọc lại từ lá số, không
    # tính lại, để chỉ một chỗ quyết định Lộc Tồn nằm đâu.
    loc_ton = anchors.get("LOC_TON")
    if loc_ton is None:
        _logger.warning("Thiếu Lộc Tồn nên không an được Quốc Ấn, Đường Phù, Hỷ Thần.")
    else:
        anchor_inputs: dict[str, object] = {"loc_ton": CHI[loc_ton]}
        an = RuleId.QUOC_AN_DUONG_PHU
        placed.append(("QUOC_AN", an, group2.place_quoc_an(loc_ton), anchor_inputs))
        placed.append(("DUONG_PHU", an, group2.place_duong_phu(loc_ton), anchor_inputs))

    for star_id, rule, branch, inputs in placed:
        star = _placed_star(star_id, CHI[branch], profile=profile, rule=rule)
        by_branch[branch].stars.append(star)
        if trace_log is not None:
            trace_log.record(profile, rule, f"{star.name} → {CHI[branch]}", **inputs)


#: Sát tinh / bại tinh nhóm 1 phụ thuộc chi năm.
_MALEFIC_FROM_YEAR_BRANCH: tuple[tuple[str, RuleId, Callable[[int], int]], ...] = (
    ("KIEP_SAT", RuleId.KIEP_SAT, malefic.place_kiep_sat),
    ("CO_THAN", RuleId.CO_THAN_QUA_TU, malefic.place_co_than),
    ("QUA_TU", RuleId.CO_THAN_QUA_TU, malefic.place_qua_tu),
    ("THIEN_KHONG", RuleId.THIEN_KHONG, malefic.place_thien_khong),
    ("THIEN_KHOC", RuleId.THIEN_KHOC_THIEN_HU, malefic.place_thien_khoc),
    ("THIEN_HU", RuleId.THIEN_KHOC_THIEN_HU, malefic.place_thien_hu),
)


def _place_malefic_stars(
    by_branch: dict[int, Palace],
    *,
    year_branch: int,
    hour_branch: int,
    cycle_forward: bool,
    profile: ConventionProfile,
    trace_log: TraceLog | None = None,
) -> None:
    """Place sát tinh / bại tinh nhóm 1.

    Six of the sixteen are members of cycles this engine already walks — vòng Thái
    Tuế and vòng Bác Sĩ — so they are read off those, not given fresh formulas.

    Nothing here decides whether a star is "good" or "bad": that is interpretation,
    and the chart's colour means ngũ hành, not fortune.
    """
    if profile.binding(RuleId.DIA_KHONG_DIA_KIEP).is_unresolved:
        return

    year_inputs: dict[str, object] = {"chi_nam": CHI[year_branch]}
    hour_inputs: dict[str, object] = {"gio_sinh": CHI[hour_branch]}
    placed: list[tuple[str, RuleId, int, dict[str, object]]] = [
        (star_id, rule, place(year_branch), year_inputs)
        for star_id, rule, place in _MALEFIC_FROM_YEAR_BRANCH
    ]

    khong_kiep = RuleId.DIA_KHONG_DIA_KIEP
    placed.append(("DIA_KIEP", khong_kiep, malefic.place_dia_kiep(hour_branch), hour_inputs))
    placed.append(("DIA_KHONG", khong_kiep, malefic.place_dia_khong(hour_branch), hour_inputs))

    hoa_linh_inputs: dict[str, object] = {
        "chi_nam": CHI[year_branch],
        "gio_sinh": CHI[hour_branch],
        "chieu": "thuận" if cycle_forward else "nghịch",
    }
    for star_id, place_hl in (
        ("HOA_TINH", malefic.place_hoa_tinh),
        ("LINH_TINH", malefic.place_linh_tinh),
    ):
        branch = place_hl(year_branch, hour_branch, forward=cycle_forward)
        placed.append((star_id, RuleId.HOA_TINH_LINH_TINH, branch, hoa_linh_inputs))

    for star_id, rule, branch, inputs in placed:
        star = _placed_star(star_id, CHI[branch], profile=profile, rule=rule)
        by_branch[branch].stars.append(star)
        if trace_log is not None:
            trace_log.record(profile, rule, f"{star.name} → {CHI[branch]}", **inputs)


def _place_star_cycles(
    by_branch: dict[int, Palace],
    *,
    year_branch: int,
    cycle_forward: bool,
    profile: ConventionProfile,
    trace_log: TraceLog | None = None,
) -> None:
    """Walk vòng Thái Tuế and vòng Bác Sĩ **once each**, placing all twelve stars.

    Before this, members of the same cycle were placed from three different call
    sites as they were requested group by group. That is how one cycle quietly
    acquires two implementations and they drift apart. A cycle is walked here, in
    one place, and every member is an offset in it.

    Vòng Thái Tuế anchors on the year branch. Vòng Bác Sĩ anchors on **Lộc Tồn**,
    which the chart already carries — read back, never recomputed.
    """
    if profile.binding(RuleId.THAI_TUE_CYCLE).is_unresolved:
        return

    placed: list[tuple[str, RuleId, int, dict[str, object]]] = []

    thai_tue_inputs: dict[str, object] = {"chi_nam": CHI[year_branch], "vong": "Thái Tuế"}
    for star_id in group2.THAI_TUE_CYCLE:
        branch = group2.place_thai_tue_member(year_branch, star_id)
        placed.append((star_id, RuleId.THAI_TUE_CYCLE, branch, thai_tue_inputs))

    loc_ton = next(
        (b for b, palace in by_branch.items() for star in palace.stars if star.id == "LOC_TON"),
        None,
    )
    if loc_ton is None:
        _logger.warning("Thiếu Lộc Tồn nên không an được vòng Bác Sĩ.")
    else:
        bac_si_inputs: dict[str, object] = {
            "loc_ton": CHI[loc_ton],
            "chieu": "thuận" if cycle_forward else "nghịch",
            "vong": "Bác Sĩ",
        }
        for star_id in group2.BAC_SI_CYCLE:
            branch = group2.place_bac_si_member(loc_ton, star_id, forward=cycle_forward)
            placed.append((star_id, RuleId.BAC_SI_CYCLE, branch, bac_si_inputs))

    for star_id, rule, branch, inputs in placed:
        star = _placed_star(star_id, CHI[branch], profile=profile, rule=rule)
        by_branch[branch].stars.append(star)
        if trace_log is not None:
            trace_log.record(profile, rule, f"{star.name} → {CHI[branch]}", **inputs)


def _place_group_3_stars(
    by_branch: dict[int, Palace],
    *,
    year_stem: int,
    year_branch: int,
    lunar_month: int,
    hour_branch: int,
    profile: ConventionProfile,
    trace_log: TraceLog | None = None,
) -> None:
    """Place phụ tinh nhóm 3 — the rules that are not offsets of an existing cycle.

    Thiên Thương and Thiên Sứ are tied to cung Nô Bộc and cung Tật Ách. The palace
    layout is already decided, so their branches are read off it; the frontend is
    never given the chance to work out where a palace is.
    """
    if profile.binding(RuleId.PHA_TOAI).is_unresolved:
        return

    year_inputs: dict[str, object] = {"chi_nam": CHI[year_branch]}
    month_inputs: dict[str, object] = {"thang_am": lunar_month}
    stem_inputs: dict[str, object] = {"can_nam": CAN[year_stem]}
    placed: list[tuple[str, RuleId, int, dict[str, object]]] = [
        ("PHA_TOAI", RuleId.PHA_TOAI, group3.place_pha_toai(year_branch), year_inputs),
        (
            "THIEN_HINH",
            RuleId.THIEN_HINH_THIEN_DIEU,
            group3.place_thien_hinh(lunar_month),
            month_inputs,
        ),
        (
            "THIEN_DIEU",
            RuleId.THIEN_HINH_THIEN_DIEU,
            group3.place_thien_dieu(lunar_month),
            month_inputs,
        ),
        (
            "THIEN_LA",
            RuleId.THIEN_LA_DIA_VONG,
            group3.THIEN_LA_BRANCH,
            {"co_dinh": "Thìn"},
        ),
        (
            "DIA_VONG",
            RuleId.THIEN_LA_DIA_VONG,
            group3.DIA_VONG_BRANCH,
            {"co_dinh": "Tuất"},
        ),
        (
            "LUU_HA",
            RuleId.LUU_HA,
            group3.place_luu_ha(year_stem),
            stem_inputs,
        ),
        (
            "THIEN_TRU",
            RuleId.THIEN_TRU,
            group3.place_thien_tru(year_stem),
            stem_inputs,
        ),
        (
            "THIEN_Y",
            RuleId.THIEN_Y,
            group3.place_thien_y(lunar_month),
            month_inputs,
        ),
        (
            "GIAI_THAN",
            RuleId.GIAI_THAN,
            group3.place_giai_than(year_branch),
            year_inputs,
        ),
        (
            "DAU_QUAN",
            RuleId.DAU_QUAN,
            group3.place_dau_quan(year_branch, lunar_month, hour_branch),
            {
                "chi_nam": CHI[year_branch],
                "thang_am": lunar_month,
                "gio_sinh": CHI[hour_branch],
            },
        ),
    ]

    by_palace = {palace.name: branch for branch, palace in by_branch.items()}
    for star_id, palace_name in (
        ("THIEN_THUONG", PalaceName.NO_BOC),
        ("THIEN_SU", PalaceName.TAT_ACH),
    ):
        branch = by_palace[palace_name]
        placed.append(
            (
                star_id,
                RuleId.THIEN_THUONG_THIEN_SU,
                branch,
                {"cung": PALACE_LABELS[palace_name]},
            )
        )

    for star_id, rule, branch, inputs in placed:
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


def _apply_star_strength(by_branch: dict[int, Palace], *, profile: ConventionProfile) -> None:
    """Attach miếu/vượng/đắc/bình/hãm by looking the star up at its own branch.

    Metadata only — no star moves. Strength is a property of *where a star already
    is*, so this runs last and reads positions rather than deciding them.

    **Hai nguồn, theo thứ tự.** Bảng của trường phái đi trước; chỗ nào bảng chưa có
    thì đọc **ô đã quan sát được từ lá số đối chiếu**. Nguồn thứ hai dùng được vì một
    ô độ sáng không phụ thuộc lá số: "Tử Vi tại Dần là Miếu" đúng ở mọi lá số có Tử Vi
    ở Dần. Đây là *một phần bảng đã đọc ra*, không phải suy đoán.

    Bảng của trường phái hiện vẫn rỗng, và đó vẫn là trạng thái đúng: một bảng sai
    trông vẫn hợp lý với người không chuyên. Khác biệt là nay có 23 ô có bằng chứng,
    nên lá số hiện được độ sáng ở đúng những ô ấy thay vì không hiện gì.
    """
    binding = profile.binding(RuleId.STAR_STRENGTH)
    if binding.is_unresolved:
        return
    table = strength.NAM_PHAI_STAR_STRENGTH_V1

    for palace in by_branch.values():
        for index, star in enumerate(palace.stars):
            value = table.strength_for(star.id, palace.branch)
            source = binding.verification
            if value is None:
                value = reference.OBSERVED_STRENGTH_CELLS.get((star.id, palace.branch))
                # Ô đọc từ lá số in: có bằng chứng, nhưng chưa ai thẩm định lá số ấy.
                source = VerificationStatus.PROVISIONAL
            # Độ sáng của Tứ Hóa: **một bảng khác**, khoá hẹp hơn — gồm cả ngôi sao
            # mang hóa. Ta đo được "hóa này, trên sao này, tại chi này"; suy rộng sang
            # một ngôi sao khác là khẳng định thứ chưa ai đo.
            hoa_strengths: tuple[tuple[Transformation, StarStrength], ...] = tuple(
                (t, observed)
                for t in star.transformations
                if (
                    observed := reference.OBSERVED_TRANSFORMATION_STRENGTH.get(
                        (t.value, star.id, palace.branch)
                    )
                )
                is not None
            )
            if value is None and not hoa_strengths:
                continue
            palace.stars[index] = replace(
                star,
                strength=value if value is not None else star.strength,
                strength_verification=(source if value is not None else star.strength_verification),
                transformation_strengths=hoa_strengths,
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
        trace_log.record(
            profile, RuleId.TU_VI_PLACEMENT, CHI[tu_vi], cuc=cuc_number, lunar_day=lunar_day
        )
    for star_id, offset in _TU_VI_CHAIN:
        branch = (tu_vi + offset) % 12
        star = _placed_star(star_id, CHI[branch], profile=profile)
        by_branch[branch].stars.append(star)
        if trace_log is not None:
            trace_log.record(
                profile,
                RuleId.MAJOR_STARS,
                f"{star.name} → {CHI[branch]}",
                chain="Tử Vi",
                anchor=CHI[tu_vi],
                offset=offset,
            )
    for star_id, offset in _THIEN_PHU_CHAIN:
        branch = (thien_phu + offset) % 12
        star = _placed_star(star_id, CHI[branch], profile=profile)
        by_branch[branch].stars.append(star)
        if trace_log is not None:
            trace_log.record(
                profile,
                RuleId.MAJOR_STARS,
                f"{star.name} → {CHI[branch]}",
                chain="Thiên Phủ",
                anchor=CHI[thien_phu],
                offset=offset,
            )
