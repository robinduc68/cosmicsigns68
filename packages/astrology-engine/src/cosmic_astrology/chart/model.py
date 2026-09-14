"""Value objects of the chart data contract.

Every field here answers one question: *what does a complete traditional Tử Vi
chart contain?* — never *what should we guess when we do not know?* A value that
the engine does not compute, or that no reviewer has signed off, is ``None``. It
is never a placeholder, never the string ``"N/A"``, and never a plausible-looking
number. See ``docs/chart-data-contract.md``.

These types hold values the calculation layer has already produced. Nothing in
this module computes astrology.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from cosmic_astrology.calendar.sexagenary import Element
from cosmic_astrology.conventions.policies import VerificationStatus

__all__ = [
    "CHART_SCHEMA_VERSION",
    "ChartIdentity",
    "PalaceCycles",
    "StarCategory",
    "TraditionalMetadata",
    "Transformation",
    "VoidMark",
]

#: Bumped when the payload shape changes. Charts persisted under an older version
#: keep their old shape on disk, so every reader has to branch on this rather than
#: assume the newest fields exist. Version 1 is every chart written before the
#: data contract was made explicit.
CHART_SCHEMA_VERSION = 2


class Transformation(StrEnum):
    """Tứ Hóa — bốn *trạng thái* một ngôi sao có thể mang, không phải bốn ngôi sao.

    Quyết định bởi thiên can năm sinh, nên chúng gắn vào ngôi sao đã an sẵn thay vì
    sinh ra sao mới. Nhân bản một ngôi sao chỉ để hiển thị trạng thái của nó sẽ làm
    mọi phép đếm sao sai.
    """

    HOA_LOC = "HOA_LOC"
    HOA_QUYEN = "HOA_QUYEN"
    HOA_KHOA = "HOA_KHOA"
    HOA_KY = "HOA_KY"

    @property
    def short_label(self) -> str:
        """Nhãn một chữ như lá số in vẫn ghi: Lộc, Quyền, Khoa, Kỵ."""
        return {
            Transformation.HOA_LOC: "Lộc",
            Transformation.HOA_QUYEN: "Quyền",
            Transformation.HOA_KHOA: "Khoa",
            Transformation.HOA_KY: "Kỵ",
        }[self]


class StarCategory(StrEnum):
    """What kind of star this is.

    Only ``MAJOR`` is produced today — the engine places the 14 chính tinh and
    nothing else. The rest of the taxonomy exists so that minor, annual and
    transformation stars arrive into a settled contract instead of forcing a
    breaking change, and so the renderer can iterate one list of stars.
    """

    MAJOR = "MAJOR"
    SUPPORTING = "SUPPORTING"
    MALEFIC = "MALEFIC"
    LITERARY = "LITERARY"
    ROMANCE = "ROMANCE"
    WEALTH = "WEALTH"
    TRANSFORMATION = "TRANSFORMATION"
    ANNUAL = "ANNUAL"
    #: A catalogued star whose category has not been settled. Not a dumping ground:
    #: a star lands here only while its classification is an open question.
    OTHER = "OTHER"


#: Display order inside a palace. Moves text on the page and implies no astrological
#: weight. Supplied by the engine so the renderer stops inventing an ordering.
_CATEGORY_PRIORITY: dict[StarCategory, int] = {
    StarCategory.MAJOR: 0,
    StarCategory.TRANSFORMATION: 1,
    StarCategory.SUPPORTING: 2,
    StarCategory.MALEFIC: 3,
    StarCategory.LITERARY: 4,
    StarCategory.ROMANCE: 5,
    StarCategory.WEALTH: 6,
    StarCategory.OTHER: 7,
    StarCategory.ANNUAL: 8,
}


def display_priority_for(category: StarCategory) -> int:
    return _CATEGORY_PRIORITY[category]


@dataclass(frozen=True, slots=True)
class ChartIdentity:
    """Which engine and which rulebook produced this chart, and when.

    ``chart_id`` is ``None`` inside the engine on purpose: identity is assigned by
    whatever stores the chart, and a calculation layer that invented its own id
    would produce a different one on every run for the same birth.
    """

    engine_version: str
    convention_profile: str
    convention_version: str
    #: False while any critical rule is still PROVISIONAL or unresolved. Taken from
    #: the convention profile's own gate — never asserted by hand.
    production_ready: bool
    #: UTC, ISO-8601. When the calculation ran, not when the person was born.
    generated_at: str
    chart_id: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "chart_id": self.chart_id,
            "engine_version": self.engine_version,
            "convention_profile": self.convention_profile,
            "convention_version": self.convention_version,
            "production_ready": self.production_ready,
            "generated_at": self.generated_at,
        }


@dataclass(frozen=True, slots=True)
class TraditionalMetadata:
    """Traditional fields a printed chart carries that this engine does not compute.

    All four are ``None`` and will stay ``None`` until each is implemented against
    a chosen source. They are present in the contract so that a consumer can tell
    "not computed" apart from "does not exist", and so adding them later is not a
    breaking change.
    """

    #: Chủ Mệnh — the star governing the Mệnh palace. Not implemented.
    chu_menh: str | None = None
    #: Chủ Thân — the star governing the Thân palace. Not implemented.
    chu_than: str | None = None
    #: Lai nhân cung. Not implemented.
    lai_nhan_cung: str | None = None
    #: Cân lượng (cân xương tính số). Not implemented.
    can_luong: str | None = None
    #: Năm xem — the year a reading is cast for. Not implemented: on its own it is
    #: just a calendar year, and it is only meaningful paired with ``tuoi_xem``.
    nam_xem: int | None = None
    #: Tuổi xem — the subject's age in that year. Not implemented: whether "age"
    #: means tuổi ta or completed years is open question Q11, and the two differ
    #: by a year, which would move every lưu niên reading.
    tuoi_xem: int | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "chu_menh": self.chu_menh,
            "chu_than": self.chu_than,
            "lai_nhan_cung": self.lai_nhan_cung,
            "can_luong": self.can_luong,
            "nam_xem": self.nam_xem,
            "tuoi_xem": self.tuoi_xem,
        }


@dataclass(frozen=True, slots=True)
class VoidMark:
    """Tuần or Triệt on a palace.

    Richer than the boolean it replaces so a reviewer can see *why* the mark is
    there. ``present`` is the only field the renderer needs; the rest is provenance.
    """

    present: bool
    verification: VerificationStatus | None = None
    #: Which rule placed it, e.g. ``"tuan/YEAR_PILLAR_DECADE"``.
    source_rule: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "present": self.present,
            "verification": self.verification.value if self.verification else None,
            "source_rule": self.source_rule,
        }


@dataclass(frozen=True, slots=True)
class PalaceCycles:
    """Đại vận / lưu niên information for one palace.

    Every field is ``None``: đại vận direction and starting age are blocked on open
    questions Q11/Q12, and nothing downstream may fill them in. Tràng sinh is not
    implemented either.
    """

    major_cycle_age_start: int | None = None
    major_cycle_age_end: int | None = None
    #: 1-based position of this palace in the đại vận walk; 1 is cung Mệnh.
    major_cycle_index: int | None = None
    #: ``"FORWARD"`` (thuận) or ``"BACKWARD"`` (nghịch). Describes the walk only —
    #: the twelve palace names never reverse with it.
    major_cycle_direction: str | None = None
    #: Which đại vận this palace is the subject of, when cycles are computed.
    major_cycle_target: int | None = None
    #: Lưu niên. Still ``None`` — blocked, and out of scope here.
    annual_target: int | None = None
    #: One of the twelve Tràng Sinh stages.
    trang_sinh_stage: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "major_cycle_age_start": self.major_cycle_age_start,
            "major_cycle_age_end": self.major_cycle_age_end,
            "major_cycle_index": self.major_cycle_index,
            "major_cycle_direction": self.major_cycle_direction,
            "major_cycle_target": self.major_cycle_target,
            "annual_target": self.annual_target,
            "trang_sinh_stage": self.trang_sinh_stage,
        }


@dataclass(frozen=True, slots=True)
class BirthInformation:
    """The birth moment as the chart reports it back.

    ``historical_utc_offset`` is separate from the requested timezone because
    Vietnam's offset has changed: a 1968 birth in Hanoi is UTC+8, not UTC+7, and a
    chart that reported only "Asia/Ho_Chi_Minh" would hide that.
    """

    full_name: str
    gender: str
    calendar_type: str
    solar_day: int
    solar_month: int
    solar_year: int
    hour: int
    minute: int
    hour_branch: str
    hour_branch_index: int
    historical_utc_offset: float
    timezone_id: str | None
    birth_place: str | None

    @property
    def local_birth_time(self) -> str:
        return f"{self.hour:02d}:{self.minute:02d}"

    def to_dict(self) -> dict[str, object]:
        return {
            # Keys kept from schema version 1 so persisted charts and the current
            # renderer keep reading the same names.
            "name": self.full_name,
            "gender": self.gender,
            "calendar_type": self.calendar_type,
            "solar": {
                "day": self.solar_day,
                "month": self.solar_month,
                "year": self.solar_year,
                "hour": self.hour,
                "minute": self.minute,
            },
            "birth_place": self.birth_place,
            "tz_offset": self.historical_utc_offset,
            "hour_branch": self.hour_branch,
            "hour_branch_index": self.hour_branch_index,
            # Added in schema version 2.
            "full_name": self.full_name,
            "local_birth_time": self.local_birth_time,
            "timezone_id": self.timezone_id,
            "historical_utc_offset": self.historical_utc_offset,
        }


@dataclass(slots=True)
class StarProvenance:
    """Where one star's placement came from, and how far it is trusted."""

    rule: str
    verification: VerificationStatus
    #: Open-question ids still blocking this rule.
    blocked_by: tuple[str, ...] = ()
    note: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "rule": self.rule,
            "verification": self.verification.value,
            "blocked_by": list(self.blocked_by),
            "note": self.note,
        }


@dataclass(slots=True)
class PalaceMetadata:
    """Room for palace facts that are neither stars nor cycles.

    Empty today. It exists so that adding one does not change the palace shape,
    and it is deliberately a plain mapping rather than a grab-bag of optional
    columns nobody can enumerate.
    """

    entries: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return dict(self.entries)


def element_label(element: Element | None) -> str | None:
    """Vietnamese name of a ngũ hành, or ``None``. Presentation-safe, not a guess."""
    if element is None:
        return None
    return {
        Element.KIM: "Kim",
        Element.MOC: "Mộc",
        Element.THUY: "Thủy",
        Element.HOA: "Hỏa",
        Element.THO: "Thổ",
    }[element]
