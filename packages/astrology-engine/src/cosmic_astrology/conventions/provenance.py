"""Where a rule comes from.

A reviewer who says "Thiên Lương is in the wrong palace" needs an answer better
than "that is what the code does". Provenance makes the honest answer available:
either a named edition and page, or an explicit admission that no source has
been chosen yet.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["SourceReference"]


@dataclass(frozen=True, slots=True)
class SourceReference:
    """A citation for one rule.

    Every field is optional because provenance is filled in progressively: a
    rule may be copied from a book long before a reviewer has signed it off.
    ``is_complete`` is what the verification gate looks at.
    """

    title: str | None = None
    edition: str | None = None
    year: int | None = None
    page: str | None = None
    verified_by: str | None = None
    verified_at: str | None = None  # ISO-8601 date
    note: str | None = None

    @property
    def has_citation(self) -> bool:
        """True once the rule can be traced to a named publication."""
        return bool(self.title and self.year)

    @property
    def is_reviewed(self) -> bool:
        """True once a named person has signed the rule off on a given date."""
        return bool(self.verified_by and self.verified_at)

    @property
    def is_complete(self) -> bool:
        return self.has_citation and self.is_reviewed

    def to_dict(self) -> dict[str, object]:
        return {
            "title": self.title,
            "edition": self.edition,
            "year": self.year,
            "page": self.page,
            "verified_by": self.verified_by,
            "verified_at": self.verified_at,
            "note": self.note,
            "has_citation": self.has_citation,
            "is_reviewed": self.is_reviewed,
        }


#: Used by every rule until Q1/Q2/Q3 are answered. Being explicit beats ``None``:
#: it distinguishes "nobody has chosen a source" from "somebody forgot the field".
NO_SOURCE_YET = SourceReference(
    note=(
        "Chưa chốt nguồn chuẩn. Chặn bởi Q1 (trường phái), Q2 (ấn bản cụ thể) "
        "và Q3 (người thẩm định) — xem docs/astrology-conventions.md mục 0."
    )
)
