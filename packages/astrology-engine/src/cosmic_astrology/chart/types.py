"""Domain types shared by the chart engine.

These are plain dataclasses on purpose: the calculation layer has no dependency
on Pydantic, FastAPI or the database. The API layer maps them to its own schemas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from cosmic_astrology.calendar.sexagenary import Element

__all__ = [
    "BirthInput",
    "CalendarType",
    "Chart",
    "EngineStage",
    "Gender",
    "Palace",
    "PalaceName",
    "Star",
    "StarKind",
    "StarStrength",
]


class Gender(StrEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class CalendarType(StrEnum):
    SOLAR = "SOLAR"
    LUNAR = "LUNAR"


class EngineStage(StrEnum):
    """How complete the produced chart is.

    ``FRAME`` — only fully verified calculations (calendar, can chi, 12 palaces,
    Mệnh/Thân, Cục). No stars are placed.
    ``PREVIEW`` — frame plus clearly-labelled provisional star placement used for
    UI development. Never enable in production.
    ``FULL`` — complete deterministic engine (not implemented yet).
    """

    FRAME = "FRAME"
    PREVIEW = "PREVIEW"
    FULL = "FULL"


class PalaceName(StrEnum):
    MENH = "MENH"
    PHU_MAU = "PHU_MAU"
    PHUC_DUC = "PHUC_DUC"
    DIEN_TRACH = "DIEN_TRACH"
    QUAN_LOC = "QUAN_LOC"
    NO_BOC = "NO_BOC"
    THIEN_DI = "THIEN_DI"
    TAT_ACH = "TAT_ACH"
    TAI_BACH = "TAI_BACH"
    TU_TUC = "TU_TUC"
    PHU_THE = "PHU_THE"
    HUYNH_DE = "HUYNH_DE"


PALACE_LABELS: dict[PalaceName, str] = {
    PalaceName.MENH: "Mệnh",
    PalaceName.PHU_MAU: "Phụ Mẫu",
    PalaceName.PHUC_DUC: "Phúc Đức",
    PalaceName.DIEN_TRACH: "Điền Trạch",
    PalaceName.QUAN_LOC: "Quan Lộc",
    PalaceName.NO_BOC: "Nô Bộc",
    PalaceName.THIEN_DI: "Thiên Di",
    PalaceName.TAT_ACH: "Tật Ách",
    PalaceName.TAI_BACH: "Tài Bạch",
    PalaceName.TU_TUC: "Tử Tức",
    PalaceName.PHU_THE: "Phu Thê",
    PalaceName.HUYNH_DE: "Huynh Đệ",
}

# Counter-clockwise order of the palaces starting from Mệnh.
PALACE_ORDER: tuple[PalaceName, ...] = (
    PalaceName.MENH,
    PalaceName.PHU_MAU,
    PalaceName.PHUC_DUC,
    PalaceName.DIEN_TRACH,
    PalaceName.QUAN_LOC,
    PalaceName.NO_BOC,
    PalaceName.THIEN_DI,
    PalaceName.TAT_ACH,
    PalaceName.TAI_BACH,
    PalaceName.TU_TUC,
    PalaceName.PHU_THE,
    PalaceName.HUYNH_DE,
)


class StarKind(StrEnum):
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    TRANSFORMATION = "TRANSFORMATION"


class StarStrength(StrEnum):
    MIEU = "MIEU"
    VUONG = "VUONG"
    DAC = "DAC"
    BINH = "BINH"
    HAM = "HAM"


@dataclass(frozen=True, slots=True)
class BirthInput:
    """Everything the engine needs about a birth moment."""

    name: str
    gender: Gender
    calendar_type: CalendarType
    day: int
    month: int
    year: int
    hour: int
    minute: int = 0
    is_leap_month: bool = False
    tz_offset: float = 7.0
    birth_place: str | None = None
    #: IANA zone (``"Asia/Ho_Chi_Minh"``). When given, and the profile selects
    #: ``IANA_HISTORICAL``, the offset is resolved from the tz database at the
    #: birth instant instead of trusting ``tz_offset``.
    timezone_id: str | None = None

    def __post_init__(self) -> None:
        if not 1 <= self.month <= 12:
            raise ValueError("Tháng sinh phải nằm trong khoảng 1–12")
        if not 1 <= self.day <= 31:
            raise ValueError("Ngày sinh phải nằm trong khoảng 1–31")
        if not 1900 <= self.year <= 2100:
            raise ValueError("Năm sinh phải nằm trong khoảng 1900–2100")
        if not 0 <= self.hour <= 23:
            raise ValueError("Giờ sinh phải nằm trong khoảng 0–23")
        if not 0 <= self.minute <= 59:
            raise ValueError("Phút sinh phải nằm trong khoảng 0–59")
        if self.is_leap_month and self.calendar_type is not CalendarType.LUNAR:
            raise ValueError("Chỉ ngày âm lịch mới có tháng nhuận")


@dataclass(frozen=True, slots=True)
class Star:
    code: str
    label: str
    kind: StarKind
    strength: StarStrength | None = None
    provisional: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "label": self.label,
            "kind": self.kind.value,
            "strength": self.strength.value if self.strength else None,
            "provisional": self.provisional,
        }


@dataclass(slots=True)
class Palace:
    name: PalaceName
    label: str
    branch_index: int
    branch: str
    stem: str
    stem_index: int
    element: Element
    nap_am: str
    is_menh: bool = False
    is_than: bool = False
    has_tuan: bool = False
    has_triet: bool = False
    stars: list[Star] = field(default_factory=list)

    @property
    def major_stars(self) -> list[Star]:
        return [s for s in self.stars if s.kind is StarKind.MAJOR]

    @property
    def is_empty_main_star(self) -> bool:
        """Vô chính diệu — no major star sits in this palace."""
        return len(self.major_stars) == 0

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name.value,
            "label": self.label,
            "branch": self.branch,
            "branch_index": self.branch_index,
            "stem": self.stem,
            "stem_index": self.stem_index,
            "element": self.element.value,
            "nap_am": self.nap_am,
            "is_menh": self.is_menh,
            "is_than": self.is_than,
            "has_tuan": self.has_tuan,
            "has_triet": self.has_triet,
            "is_empty_main_star": self.is_empty_main_star,
            "major_stars": [s.to_dict() for s in self.stars if s.kind is StarKind.MAJOR],
            "minor_stars": [s.to_dict() for s in self.stars if s.kind is StarKind.MINOR],
            "transformations": [
                s.to_dict() for s in self.stars if s.kind is StarKind.TRANSFORMATION
            ],
        }


@dataclass(slots=True)
class Chart:
    """Structured, serialisable output of the calculation layer."""

    engine_stage: EngineStage
    engine_version: str
    #: Immutable stamp of the convention profile this chart was built under.
    #: A later engine release may compute charts differently; without this
    #: stamp there would be no way to tell an old chart apart from a new one.
    convention_profile: str
    convention_version: str
    convention_rules: list[dict[str, object]]
    timezone: dict[str, object]
    date_resolution: dict[str, object]
    trace: dict[str, object] | None
    birth: dict[str, object]
    lunar_birth: dict[str, object]
    pillars: dict[str, object]
    yin_yang: dict[str, object]
    menh: dict[str, object]
    than: dict[str, object]
    cuc: dict[str, object]
    palaces: list[Palace]

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "engine": {
                "stage": self.engine_stage.value,
                "version": self.engine_version,
                "is_authoritative": self.engine_stage is EngineStage.FULL,
                "convention_profile": self.convention_profile,
                "convention_version": self.convention_version,
            },
            "convention": {
                "profile": self.convention_profile,
                "version": self.convention_version,
                "rules": self.convention_rules,
            },
            "timezone": self.timezone,
            "date_resolution": self.date_resolution,
            "birth": self.birth,
            "lunar_birth": self.lunar_birth,
            "pillars": self.pillars,
            "yin_yang": self.yin_yang,
            "menh": self.menh,
            "than": self.than,
            "cuc": self.cuc,
            "palaces": [p.to_dict() for p in self.palaces],
            # Reserved for the full engine — kept in the payload so that the API
            # contract and the UI do not change when the engine is completed.
            "major_cycles": [],
            "annual_cycles": [],
            "four_transformations": {},
        }
        if self.trace is not None:
            payload["trace"] = self.trace
        return payload
