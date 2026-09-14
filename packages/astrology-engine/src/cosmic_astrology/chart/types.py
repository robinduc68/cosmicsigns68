"""Domain types shared by the chart engine.

These are plain dataclasses on purpose: the calculation layer has no dependency
on Pydantic, FastAPI or the database. The API layer maps them to its own schemas.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import StrEnum

from cosmic_astrology.calendar.sexagenary import Element
from cosmic_astrology.chart.model import (
    CHART_SCHEMA_VERSION,
    BirthInformation,
    ChartIdentity,
    PalaceCycles,
    PalaceMetadata,
    StarCategory,
    StarProvenance,
    TraditionalMetadata,
    Transformation,
    VoidMark,
    display_priority_for,
    rule_fingerprint,
)
from cosmic_astrology.conventions.policies import VerificationStatus
from cosmic_astrology.stars.catalog import Polarity

__all__ = [
    "BirthInput",
    "CalendarType",
    "Chart",
    "EngineStage",
    "Gender",
    "Palace",
    "PalaceName",
    "Star",
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

# Palaces from Mệnh in clockwise (thuận) order on the địa bàn: Phụ Mẫu is one step
# clockwise of Mệnh, Huynh Đệ one step counter-clockwise.
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
    """One star, whatever its category.

    There is deliberately a single star model rather than a major/minor/annual
    trio: those differ only by ``category``, and three near-identical shapes would
    force the renderer to branch on type instead of iterating.

    Every astrology field is nullable. ``strength`` is ``None`` for every star
    today — the miếu/vượng/đắc/bình/hãm table is 168 cells that must be copied
    from a chosen source, and a guessed strength is worse than no strength.
    """

    id: str
    name: str
    category: StarCategory
    #: Ngũ hành of the star itself, from ``stars.catalog``. ``None`` where the
    #: schools disagree — the renderer then draws neutral ink rather than a guess.
    element: Element | None = None
    #: Âm/dương of the star. Recorded with the element or not at all.
    polarity: Polarity | None = None
    strength: StarStrength | None = None
    #: How far the strength value is trusted. ``None`` exactly when there is no
    #: strength, so a reader can never mistake "unknown" for "verified".
    strength_verification: VerificationStatus | None = None
    #: Địa chi the star sits on. Denormalised from the palace so a flat list of
    #: stars is still self-describing.
    palace_branch: str | None = None
    #: Where the placement came from and how far it is trusted.
    provenance: StarProvenance | None = None
    #: Tứ Hóa this star carries. A tuple rather than a single value because the
    #: model must survive a future where đại vận and lưu niên each add their own
    #: hóa to the same star; today the engine only attaches the birth-year one.
    transformations: tuple[Transformation, ...] = ()

    def __post_init__(self) -> None:
        if (self.strength is None) != (self.strength_verification is None):
            raise ValueError(
                f"{self.name}: độ sáng và trạng thái kiểm định của nó phải cùng có "
                "hoặc cùng thiếu — nếu không thì 'chưa biết' sẽ bị đọc thành 'đã kiểm'."
            )

    @property
    def is_major(self) -> bool:
        return self.category is StarCategory.MAJOR

    @property
    def is_annual(self) -> bool:
        return self.category is StarCategory.ANNUAL

    @property
    def is_transformation(self) -> bool:
        """Whether the star's own **category** is TRANSFORMATION.

        Not the same as carrying a Tứ Hóa — see ``has_transformation``. Nothing is
        placed with this category today: Tứ Hóa attaches to an existing star rather
        than adding a fifth one, so a chart's star count does not change with the
        birth year.
        """
        return self.category is StarCategory.TRANSFORMATION

    @property
    def has_transformation(self) -> bool:
        return bool(self.transformations)

    def with_transformation(self, transformation: Transformation) -> Star:
        """A copy carrying one more hóa. Duplicates are refused, not ignored.

        Two rules pointing the same hóa at the same star means the table is wrong,
        and silently de-duplicating would hide that.
        """
        if transformation in self.transformations:
            raise ValueError(f"{self.name} đã mang {transformation.value} rồi")
        return replace(self, transformations=(*self.transformations, transformation))

    @property
    def verification_status(self) -> VerificationStatus:
        """Trust in this star's placement. Unverified until provenance says more."""
        return self.provenance.verification if self.provenance else VerificationStatus.UNVERIFIED

    @property
    def provisional(self) -> bool:
        """Kept as a derived flag: the renderer marks these with a warning badge."""
        return self.verification_status is not VerificationStatus.VERIFIED

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.value,
            "element": self.element.value if self.element else None,
            "polarity": self.polarity.value if self.polarity else None,
            "strength": self.strength.value if self.strength else None,
            "strength_verification": (
                self.strength_verification.value if self.strength_verification else None
            ),
            "palace_branch": self.palace_branch,
            "is_major": self.is_major,
            "is_annual": self.is_annual,
            "is_transformation": self.is_transformation,
            "has_transformation": self.has_transformation,
            "transformations": [t.value for t in self.transformations],
            "display_priority": display_priority_for(self.category),
            "verification_status": self.verification_status.value,
            "provenance": self.provenance.to_dict() if self.provenance else None,
            "provisional": self.provisional,
        }


@dataclass(slots=True)
class Palace:
    """One of the twelve palaces.

    ``branch`` and ``name`` are different concepts and must stay that way:
    ``branch`` is *where* on the địa bàn this cell is, ``name`` is *which palace*
    the chart assigns there. Deriving one from the other is what produced the
    mirrored-palace bug fixed in engine 0.2.0.
    """

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
    #: Lunar month this palace counts as. Not implemented — depends on đại vận
    #: numbering, which is blocked on Q11/Q12.
    month_number: int | None = None
    tuan: VoidMark = field(default_factory=lambda: VoidMark(present=False))
    triet: VoidMark = field(default_factory=lambda: VoidMark(present=False))
    cycles: PalaceCycles = field(default_factory=PalaceCycles)
    metadata: PalaceMetadata = field(default_factory=PalaceMetadata)
    stars: list[Star] = field(default_factory=list)

    @property
    def palace_index(self) -> int:
        """Position of this palace name in the classical sequence from Mệnh (0-11).

        Derived from ``PALACE_ORDER``, not from the branch, so it carries the
        palace assignment rather than the screen position.
        """
        return PALACE_ORDER.index(self.name)

    @property
    def has_tuan(self) -> bool:
        return self.tuan.present

    @property
    def has_triet(self) -> bool:
        return self.triet.present

    def stars_in(self, category: StarCategory) -> list[Star]:
        return [s for s in self.stars if s.category is category]

    @property
    def major_stars(self) -> list[Star]:
        return self.stars_in(StarCategory.MAJOR)

    @property
    def annual_stars(self) -> list[Star]:
        return self.stars_in(StarCategory.ANNUAL)

    @property
    def minor_stars(self) -> list[Star]:
        """Everything that is neither a chính tinh nor a hóa nor a lưu star.

        A display grouping, not a category: the categories themselves stay on each
        star so nothing is lost by grouping them here.
        """
        excluded = {StarCategory.MAJOR, StarCategory.TRANSFORMATION, StarCategory.ANNUAL}
        return [s for s in self.stars if s.category not in excluded]

    @property
    def transformations(self) -> list[Star]:
        return self.stars_in(StarCategory.TRANSFORMATION)

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
            # Grouped for the renderer, which lays out chính tinh and phụ tinh
            # differently. `stars` below is the same set, flat and ungrouped.
            "major_stars": [s.to_dict() for s in self.major_stars],
            "minor_stars": [s.to_dict() for s in self.minor_stars],
            "transformations": [s.to_dict() for s in self.transformations],
            # Added in schema version 2.
            "id": self.name.value,
            "palace_index": self.palace_index,
            "month_number": self.month_number,
            "annual_stars": [s.to_dict() for s in self.annual_stars],
            "stars": [s.to_dict() for s in self.stars],
            "tuan": self.tuan.to_dict(),
            "triet": self.triet.to_dict(),
            "cycles": self.cycles.to_dict(),
            "metadata": self.metadata.to_dict(),
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
    birth: BirthInformation
    lunar_birth: dict[str, object]
    pillars: dict[str, object]
    yin_yang: dict[str, object]
    #: Mệnh palace: branch, bản mệnh element and nạp âm, tam phương tứ chính.
    menh: dict[str, object]
    #: Thân palace: branch and which palace it resides in (thân cư).
    than: dict[str, object]
    #: Cục number, its element, and the Mệnh–Cục relationship.
    cuc: dict[str, object]
    palaces: list[Palace]
    #: When the calculation ran. Injected rather than read from the clock here, so
    #: the same birth plus the same timestamp always serialises identically.
    generated_at: str
    production_ready: bool
    traditional: TraditionalMetadata = field(default_factory=TraditionalMetadata)

    @property
    def identity(self) -> ChartIdentity:
        return ChartIdentity(
            engine_version=self.engine_version,
            convention_profile=self.convention_profile,
            convention_version=self.convention_version,
            production_ready=self.production_ready,
            generated_at=self.generated_at,
            rule_fingerprint=self.rule_fingerprint,
        )

    @property
    def rule_fingerprint(self) -> str:
        """Vân tay của tập sao thực tế trên lá số này và tập luật đã dùng."""
        return rule_fingerprint(
            (star.id for star in self.stars),
            (
                (str(rule["rule"]), str(rule["policy"]))
                for rule in self.convention_rules
                if rule.get("implemented")
            ),
        )

    @property
    def stars(self) -> list[Star]:
        """Every star on the chart, flat. Each one still names its own palace."""
        return [star for palace in self.palaces for star in palace.stars]

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "schema_version": CHART_SCHEMA_VERSION,
            "identity": self.identity.to_dict(),
            "traditional": self.traditional.to_dict(),
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
            "birth": self.birth.to_dict(),
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
