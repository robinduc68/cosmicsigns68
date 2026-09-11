"""Ngũ hành and âm/dương of each star.

This is astrology metadata, not a rendering concern: the renderer is handed
``star.element`` and only turns it into a colour. Nothing here may be inferred
from a star's name at display time.

**Why several stars carry no element.** The ngũ hành of the 14 chính tinh is not
uniform across schools. Where the classical texts read the same way, the value is
recorded below as ``PROVISIONAL`` — the same standing the 14 placements already
have. Where they genuinely disagree, ``element`` stays ``None`` and the star
renders in neutral ink. Guessing to make the chart colourful would put a claim on
a customer's chart that no source backs, which is the one failure mode this
project refuses; the alternatives are written down instead so a reviewer can
settle them through the verification workbench.

No entry here is ``VERIFIED``: ``tests/fixtures/sources.json`` has no primary
reference selected yet (Q1/Q2/Q3 in ``docs/astrology-conventions.md``). Promotion
happens through the review workflow, never by editing this table.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType

from cosmic_astrology.calendar.sexagenary import Element

__all__ = [
    "STAR_METADATA",
    "ElementCoverage",
    "Polarity",
    "StarMetadata",
    "element_coverage",
    "metadata_for",
]


class Polarity(StrEnum):
    """Âm/dương of a star. Rendered as a ``+``/``−`` prefix; never a colour."""

    YANG = "YANG"
    YIN = "YIN"


@dataclass(frozen=True, slots=True)
class StarMetadata:
    """What one star is, with the provenance of that claim attached.

    ``element`` and ``polarity`` are both optional and move together: the classical
    sources state them as a single phrase ("âm thủy"), so when that phrase is
    disputed neither half is recorded.
    """

    code: str
    label: str
    element: Element | None
    polarity: Polarity | None
    #: Why this reading was recorded, or why nothing was.
    note: str
    #: Competing readings found in other schools. Never silently merged.
    alternatives: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        # Enforced on the type, not in a helper, so no future entry can slip past it.
        if (self.element is None) != (self.polarity is None):
            raise ValueError(
                f"{self.label}: ngũ hành và âm/dương phải cùng có hoặc cùng thiếu — "
                "chúng đến từ cùng một câu trong sách."
            )
        if not self.note.strip():
            raise ValueError(f"{self.label}: phải ghi lý do cho giá trị (hoặc cho việc để trống).")
        if self.element is None and len(self.alternatives) < 2:
            raise ValueError(
                f"{self.label}: để trống ngũ hành thì phải liệt kê các cách đọc đang "
                "mâu thuẫn, nếu không thì đó là im lặng chứ không phải ghi nhận."
            )

    @property
    def has_element(self) -> bool:
        return self.element is not None


def _star(
    code: str,
    label: str,
    element: Element | None,
    polarity: Polarity | None,
    note: str,
    alternatives: tuple[str, ...] = (),
) -> StarMetadata:
    return StarMetadata(code, label, element, polarity, note, alternatives)


#: The 14 chính tinh. Codes match ``chart.builder._TU_VI_CHAIN`` /
#: ``_THIEN_PHU_CHAIN`` — a test asserts the two stay in step.
_MAJOR: tuple[StarMetadata, ...] = (
    _star("TU_VI", "Tử Vi", Element.THO, Polarity.YIN, "Âm thổ — nhất quán giữa các sách."),
    _star("THIEN_CO", "Thiên Cơ", Element.MOC, Polarity.YIN, "Âm mộc — nhất quán."),
    _star("THAI_DUONG", "Thái Dương", Element.HOA, Polarity.YANG, "Dương hỏa — nhất quán."),
    _star("VU_KHUC", "Vũ Khúc", Element.KIM, Polarity.YIN, "Âm kim — nhất quán."),
    _star("THIEN_DONG", "Thiên Đồng", Element.THUY, Polarity.YANG, "Dương thủy — nhất quán."),
    _star(
        "LIEM_TRINH",
        "Liêm Trinh",
        Element.KIM,
        Polarity.YIN,
        "Âm kim — đa số sách Đẩu Số ghi vậy (hóa khí là tù).",
        ("Một số bản Việt ghi Hỏa; cần bản in cụ thể để chốt.",),
    ),
    _star("THIEN_PHU", "Thiên Phủ", Element.THO, Polarity.YANG, "Dương thổ — nhất quán."),
    _star("THAI_AM", "Thái Âm", Element.THUY, Polarity.YIN, "Âm thủy — nhất quán."),
    _star(
        "THAM_LANG",
        "Tham Lang",
        None,
        None,
        "CHƯA GHI NHẬN. Sách cổ ghi 'âm thủy, hóa khí là mộc' — hai hành trong cùng "
        "một câu, nên không có một đáp án đơn trị để tô màu.",
        ("Thủy (bản thể)", "Mộc (hóa khí)"),
    ),
    _star(
        "CU_MON",
        "Cự Môn",
        None,
        None,
        "CHƯA GHI NHẬN. Các trường phái ghi khác nhau rõ rệt, chưa có nguồn chuẩn để chọn.",
        ("Thổ (đa số bản Hoa)", "Thủy (một số bản Việt)", "Kim (thiểu số)"),
    ),
    _star("THIEN_TUONG", "Thiên Tướng", Element.THUY, Polarity.YANG, "Dương thủy — nhất quán."),
    _star(
        "THIEN_LUONG",
        "Thiên Lương",
        Element.THO,
        Polarity.YANG,
        "Dương thổ — đa số sách ghi vậy.",
        ("Một số bản suy từ chữ 梁 (rường gỗ) mà ghi Mộc.",),
    ),
    _star("THAT_SAT", "Thất Sát", Element.KIM, Polarity.YANG, "Dương kim — nhất quán."),
    _star("PHA_QUAN", "Phá Quân", Element.THUY, Polarity.YIN, "Âm thủy — nhất quán."),
)

#: Read-only so no caller can reach in and add a star at runtime.
STAR_METADATA: Mapping[str, StarMetadata] = MappingProxyType({s.code: s for s in _MAJOR})


def metadata_for(code: str) -> StarMetadata | None:
    """Metadata for a star code, or ``None`` when the star is not catalogued yet.

    ``None`` is a normal answer, not a failure: the engine places only the 14
    chính tinh today, and every other star will arrive uncatalogued first.
    """
    return STAR_METADATA.get(code)


@dataclass(frozen=True, slots=True)
class ElementCoverage:
    """How much of the catalogue actually carries a ngũ hành.

    Counted from the table, never estimated, so the number in the report cannot
    drift away from the data.
    """

    total: int
    with_element: int
    missing: tuple[str, ...]

    @property
    def percentage(self) -> float:
        return 0.0 if self.total == 0 else round(self.with_element / self.total * 100, 1)

    def to_dict(self) -> dict[str, object]:
        return {
            "total": self.total,
            "with_element": self.with_element,
            "missing": list(self.missing),
            "percentage": self.percentage,
        }


def element_coverage() -> ElementCoverage:
    entries = tuple(STAR_METADATA.values())
    missing = tuple(e.label for e in entries if not e.has_element)
    return ElementCoverage(
        total=len(entries),
        with_element=sum(1 for e in entries if e.has_element),
        missing=missing,
    )
