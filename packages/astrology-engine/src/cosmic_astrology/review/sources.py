"""Citations, held once and referenced by many fixtures.

Cosmic Signs does not decide that one book is universally right — that is a
judgement for a practitioner, not for code. What the code does is let a reviewer
*label* how a source is being used, so a chart verified against a cross-check
can never be mistaken for one verified against the selected reference.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

__all__ = ["Source", "SourceRegistry", "SourceType"]


class SourceType(StrEnum):
    """How a reviewer is using a source — not a ranking of truth."""

    #: The one reference the Cosmic Signs convention will eventually point at.
    PRIMARY_SELECTED_REFERENCE = "PRIMARY_SELECTED_REFERENCE"
    SECONDARY_REFERENCE = "SECONDARY_REFERENCE"
    CROSS_CHECK_REFERENCE = "CROSS_CHECK_REFERENCE"
    #: A practising astrologer casting the chart by hand.
    PRACTITIONER_VERIFICATION = "PRACTITIONER_VERIFICATION"


@dataclass(frozen=True, slots=True)
class Source:
    id: str
    title: str
    source_type: SourceType
    author: str | None = None
    edition: str | None = None
    publication_year: int | None = None
    publisher: str | None = None
    school: str | None = None
    notes: str = ""

    @property
    def is_citable(self) -> bool:
        """Enough detail for someone else to find the same page.

        A practitioner verification is citable without a publication year — the
        person *is* the source — but it must name a school, or "verified by an
        expert" says nothing about which tradition was applied.
        """
        if self.source_type is SourceType.PRACTITIONER_VERIFICATION:
            return bool(self.title and self.school)
        return bool(self.title and self.publication_year)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "title": self.title,
            "source_type": self.source_type.value,
            "author": self.author,
            "edition": self.edition,
            "publication_year": self.publication_year,
            "publisher": self.publisher,
            "school": self.school,
            "notes": self.notes,
            "is_citable": self.is_citable,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> Source:
        return cls(
            id=str(raw["id"]),
            title=str(raw["title"]),
            source_type=SourceType(str(raw["source_type"])),
            author=_opt_str(raw.get("author")),
            edition=_opt_str(raw.get("edition")),
            publication_year=int(raw["publication_year"])
            if raw.get("publication_year") is not None
            else None,
            publisher=_opt_str(raw.get("publisher")),
            school=_opt_str(raw.get("school")),
            notes=str(raw.get("notes") or ""),
        )


def _opt_str(value: object) -> str | None:
    return None if value is None else str(value)


@dataclass(slots=True)
class SourceRegistry:
    """Sources keyed by id, so a citation is written once and reused."""

    sources: dict[str, Source] = field(default_factory=dict)

    def get(self, source_id: str | None) -> Source | None:
        return self.sources.get(source_id) if source_id else None

    def add(self, source: Source) -> None:
        self.sources[source.id] = source

    @property
    def primary(self) -> Source | None:
        """The selected reference, once a reviewer has designated one."""
        for source in self.sources.values():
            if source.source_type is SourceType.PRIMARY_SELECTED_REFERENCE:
                return source
        return None

    def to_dict(self) -> dict[str, object]:
        return {
            "sources": [s.to_dict() for s in self.sources.values()],
            "primary_selected_reference": self.primary.id if self.primary else None,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> SourceRegistry:
        entries = raw.get("sources") or []
        registry = cls()
        for entry in entries:
            source = Source.from_dict(entry)
            registry.add(source)
        return registry
