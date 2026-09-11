"""A recorded disagreement between the engine and a source.

When a reviewer finds the engine placing a star elsewhere than the reference
does, the answer is not to edit the formula until it agrees. It is to write the
disagreement down, with both positions and the citation, and decide separately —
possibly the engine is wrong, possibly the source follows another school.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

__all__ = ["Discrepancy", "DiscrepancyStatus"]


class DiscrepancyStatus(StrEnum):
    OPEN = "OPEN"
    #: Investigated and judged a difference of school, not an error.
    ACCEPTED_SCHOOL_DIFFERENCE = "ACCEPTED_SCHOOL_DIFFERENCE"
    #: The engine is wrong and a fix is owed. Fixing happens in its own change.
    ENGINE_BUG_CONFIRMED = "ENGINE_BUG_CONFIRMED"
    #: The expected value was mis-entered.
    REVIEW_ERROR = "REVIEW_ERROR"
    RESOLVED = "RESOLVED"


@dataclass(frozen=True, slots=True)
class Discrepancy:
    id: str
    fixture_id: str
    rule_id: str
    subject: str
    candidate: str | None
    expected: str | None
    source_id: str | None
    reviewer: str | None
    recorded_at: str | None
    notes: str = ""
    status: DiscrepancyStatus = DiscrepancyStatus.OPEN

    @property
    def is_blocking(self) -> bool:
        """Only an unresolved disagreement blocks a rule from being promoted."""
        return self.status in (DiscrepancyStatus.OPEN, DiscrepancyStatus.ENGINE_BUG_CONFIRMED)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "fixture_id": self.fixture_id,
            "rule_id": self.rule_id,
            "subject": self.subject,
            "candidate": self.candidate,
            "expected": self.expected,
            "source_id": self.source_id,
            "reviewer": self.reviewer,
            "recorded_at": self.recorded_at,
            "notes": self.notes,
            "status": self.status.value,
            "is_blocking": self.is_blocking,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, object]) -> Discrepancy:
        return cls(
            id=str(raw["id"]),
            fixture_id=str(raw["fixture_id"]),
            rule_id=str(raw["rule_id"]),
            subject=str(raw.get("subject") or ""),
            candidate=_opt(raw.get("candidate")),
            expected=_opt(raw.get("expected")),
            source_id=_opt(raw.get("source_id")),
            reviewer=_opt(raw.get("reviewer")),
            recorded_at=_opt(raw.get("recorded_at")),
            notes=str(raw.get("notes") or ""),
            status=DiscrepancyStatus(str(raw.get("status", DiscrepancyStatus.OPEN.value))),
        )


def _opt(value: object) -> str | None:
    return None if value is None else str(value)
