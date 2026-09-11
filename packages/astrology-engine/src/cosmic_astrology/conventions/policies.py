"""Every school-dependent choice the engine makes, named and enumerated.

The point of this module is negative: after it exists, a Tử Vi rule that varies
between schools may **not** live as an unnamed branch inside calculation code.
It has to be a policy value here, selected by a convention profile, so that two
charts built under different assumptions can never be mistaken for each other.

Policies whose value is ``UNRESOLVED`` are open questions (see
``docs/astrology-conventions.md``). They are not defaults and not placeholders
to be quietly filled in: asking the engine to apply one is an error.
"""

from __future__ import annotations

from enum import StrEnum

__all__ = [
    "BirthTimeCorrectionPolicy",
    "CalendarPolicy",
    "CucPolicy",
    "DayBoundaryPolicy",
    "FourTransformationsPolicy",
    "LateZiPolicy",
    "MajorCycleDirectionPolicy",
    "MajorCycleStartAgePolicy",
    "MajorStarPolicy",
    "MenhPolicy",
    "PalaceOrderPolicy",
    "PalaceStemPolicy",
    "RuleId",
    "StarStrengthPolicy",
    "ThanPolicy",
    "TimezonePolicy",
    "TrietPolicy",
    "TuViPolicy",
    "TuanPolicy",
    "VerificationStatus",
    "YinYangPolicy",
]

UNRESOLVED = "UNRESOLVED"


class RuleId(StrEnum):
    """Stable identifiers for the rules a profile has to pin down."""

    CALENDAR = "calendar"
    TIMEZONE = "timezone"
    BIRTH_TIME_CORRECTION = "birth_time_correction"
    DAY_BOUNDARY = "day_boundary"
    LATE_ZI = "late_zi"
    YIN_YANG = "yin_yang"
    MENH_PLACEMENT = "menh_placement"
    THAN_PLACEMENT = "than_placement"
    CUC = "cuc"
    PALACE_ORDER = "palace_order"
    PALACE_STEMS = "palace_stems"
    TU_VI_PLACEMENT = "tu_vi_placement"
    MAJOR_STARS = "major_stars"
    STAR_ELEMENTS = "star_elements"
    FOUR_TRANSFORMATIONS = "four_transformations"
    TUAN = "tuan"
    TRIET = "triet"
    STAR_STRENGTH = "star_strength"
    TRANG_SINH_START = "trang_sinh_start"
    TRANG_SINH_DIRECTION = "trang_sinh_direction"
    MAJOR_CYCLE_DIRECTION = "major_cycle_direction"
    MAJOR_CYCLE_START_AGE = "major_cycle_start_age"


class VerificationStatus(StrEnum):
    """How much trust a rule has earned.

    Deliberately separate from "is it implemented". A rule can be fully coded and
    still be ``PROVISIONAL`` — that is exactly the state the 14 major stars are
    in today, and conflating the two is how an unverified chart ends up being
    presented as authoritative.
    """

    UNVERIFIED = "UNVERIFIED"
    PROVISIONAL = "PROVISIONAL"
    VERIFIED = "VERIFIED"


class CalendarPolicy(StrEnum):
    MEEUS_CH49_VIETNAM = "MEEUS_CH49_VIETNAM"


class TimezonePolicy(StrEnum):
    """Where the UTC offset of the birth moment comes from."""

    #: Resolve from the IANA database at the birth instant. Correct across the
    #: historical offset changes Vietnam went through.
    IANA_HISTORICAL = "IANA_HISTORICAL"
    #: Caller supplies a fixed offset. Kept for explicit, deliberate overrides.
    FIXED_OFFSET = "FIXED_OFFSET"


class BirthTimeCorrectionPolicy(StrEnum):
    """Whether clock time is corrected towards local solar time.

    Distinct from :class:`TimezonePolicy` on purpose: a timezone answers "what
    did the clock on the wall read", a correction answers "where was the sun".
    Conflating them is a common way to be wrong twice.
    """

    NONE = "NONE"
    #: Not implemented — the convention has to define the exact correction first.
    TRUE_SOLAR_TIME = "TRUE_SOLAR_TIME"


class DayBoundaryPolicy(StrEnum):
    LOCAL_MIDNIGHT = "LOCAL_MIDNIGHT"


class LateZiPolicy(StrEnum):
    """What a birth at 23:00–23:59 belongs to. **Open question Q6.**

    Giờ Tý straddles midnight, so a birth in its first half can be argued to
    belong to either civil day. The three positions below are all held by real
    schools; the engine refuses to guess between them.
    """

    #: No policy chosen. Asking the engine to place a late-Zi birth raises.
    UNRESOLVED = UNRESOLVED
    #: 23:xx stays on the current civil day for everything.
    CIVIL_DAY = "CIVIL_DAY"
    #: 23:xx belongs to the next day for everything — lunar day and day pillar.
    LATE_ZI_NEXT_DAY = "LATE_ZI_NEXT_DAY"
    #: Day pillar advances, the lunar day used for star placement does not.
    #: Asymmetric by design, not by accident — see docs before selecting it.
    PILLAR_ONLY_NEXT_DAY = "PILLAR_ONLY_NEXT_DAY"


class YinYangPolicy(StrEnum):
    YEAR_STEM_PARITY = "YEAR_STEM_PARITY"


class MenhPolicy(StrEnum):
    #: From Dần, forward to the lunar month, then backward by the hour branch.
    DAN_FORWARD_MONTH_BACKWARD_HOUR = "DAN_FORWARD_MONTH_BACKWARD_HOUR"


class ThanPolicy(StrEnum):
    #: From Dần, forward to the lunar month, then forward by the hour branch.
    DAN_FORWARD_MONTH_FORWARD_HOUR = "DAN_FORWARD_MONTH_FORWARD_HOUR"


class CucPolicy(StrEnum):
    #: Cục from the nạp âm of the Mệnh palace's stem+branch.
    NAP_AM_OF_MENH_PALACE = "NAP_AM_OF_MENH_PALACE"


class PalaceOrderPolicy(StrEnum):
    """How the twelve palace names are laid onto the địa chi.

    The value name is kept as stored in existing charts. It describes the classical
    sequence Mệnh → Huynh Đệ → Phu Thê → Tử Tức → Tài Bạch → Tật Ách → Thiên Di →
    Nô Bộc → Quan Lộc → Điền Trạch → Phúc Đức → Phụ Mẫu walking counter-clockwise,
    which puts Phụ Mẫu one step *clockwise* of Mệnh.
    """

    COUNTER_CLOCKWISE_FROM_MENH = "COUNTER_CLOCKWISE_FROM_MENH"


class PalaceStemPolicy(StrEnum):
    NGU_HO_DON = "NGU_HO_DON"


class TuViPolicy(StrEnum):
    #: Classical cục-remainder walk from Dần.
    CUC_REMAINDER_CLASSICAL = "CUC_REMAINDER_CLASSICAL"


class MajorStarPolicy(StrEnum):
    #: Tử Vi chain counter-clockwise, Thiên Phủ chain clockwise about Dần–Thân.
    TWO_CHAINS_CLASSICAL = "TWO_CHAINS_CLASSICAL"


class FourTransformationsPolicy(StrEnum):
    """**Open questions Q7/Q8.** The Canh row alone has three recorded variants."""

    UNRESOLVED = UNRESOLVED


class TuanPolicy(StrEnum):
    YEAR_PILLAR_DECADE = "YEAR_PILLAR_DECADE"


class TrietPolicy(StrEnum):
    #: Table by year stem, both branches weighted equally. **Q10** asks whether
    #: the two branches should carry different weight.
    YEAR_STEM_TABLE_EQUAL_WEIGHT = "YEAR_STEM_TABLE_EQUAL_WEIGHT"


class StarElementPolicy(StrEnum):
    """Where a star's own ngũ hành comes from.

    Separate from ``STAR_STRENGTH``: strength is a 14 × 12 table that depends on
    the palace, while a star's element is a property of the star alone. Recorded
    only where the classical readings agree — the rest stay empty on purpose, so
    this policy is *partial* by name and cannot be mistaken for complete.
    """

    CLASSICAL_CONSENSUS_PARTIAL = "CLASSICAL_CONSENSUS_PARTIAL"


class StarStrengthPolicy(StrEnum):
    """**Open question, blocked on Q1/Q2.**

    The miếu/vượng/đắc/bình/hãm table is 14 stars × 12 branches and cannot be
    derived from any formula — it has to be copied from a named source. There is
    deliberately no default value here.
    """

    UNRESOLVED = UNRESOLVED


class TrangSinhStartPolicy(StrEnum):
    """Which branch vòng Tràng Sinh begins on, given the ngũ hành of the Cục.

    Kim → Tỵ, Mộc → Hợi, Thủy → Thân, Hỏa → Dần are read the same way everywhere.
    **Thổ is not**, and the two readings move the whole cycle by six branches for
    every Thổ Ngũ Cục chart, so the choice cannot be left implicit.
    """

    #: Thổ starts where Thủy does (Thân). The majority reading in Vietnamese texts.
    CUC_ELEMENT_THO_WITH_THUY = "CUC_ELEMENT_THO_WITH_THUY"
    #: Thổ starts where Hỏa does (Dần).
    CUC_ELEMENT_THO_WITH_HOA = "CUC_ELEMENT_THO_WITH_HOA"


class TrangSinhDirectionPolicy(StrEnum):
    """Which way vòng Tràng Sinh runs around the địa bàn.

    The two readings disagree on half of all charts, so this is not a detail.
    """

    #: Dương nam and âm nữ thuận; âm nam and dương nữ nghịch — the same rule as
    #: đại vận. The majority reading.
    YANG_MALE_YIN_FEMALE_FORWARD = "YANG_MALE_YIN_FEMALE_FORWARD"
    #: Direction taken from the âm dương of the Cục instead of the subject.
    CUC_POLARITY = "CUC_POLARITY"


class MajorCycleDirectionPolicy(StrEnum):
    YANG_MALE_YIN_FEMALE_FORWARD = "YANG_MALE_YIN_FEMALE_FORWARD"


class MajorCycleStartAgePolicy(StrEnum):
    """Which age the first đại vận starts at.

    The sources agree it is the Cục number. What they do not settle is **what an
    age counts** — tuổi ta or completed years — which is open question **Q11**.
    That distinction does not change any number below; it changes how an age maps
    to a calendar year, which is why lưu niên stays blocked.
    """

    CUC_NUMBER = "CUC_NUMBER"
    UNRESOLVED = UNRESOLVED
