"""Review states, and the rules that decide when one may be claimed.

The central invariant: a fixture is VERIFIED because a person went to a source
and wrote down what it says — never because the engine's numbers looked
plausible, and never because a test passed.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from cosmic_astrology.review.sources import Source

__all__ = [
    "MAJOR_STAR_CODES",
    "FixtureReview",
    "ReviewState",
    "StarComparison",
    "compare_stars",
    "evaluate_state",
]

MAJOR_STAR_CODES: tuple[str, ...] = (
    "TU_VI", "THIEN_CO", "THAI_DUONG", "VU_KHUC", "THIEN_DONG", "LIEM_TRINH",
    "THIEN_PHU", "THAI_AM", "THAM_LANG", "CU_MON", "THIEN_TUONG", "THIEN_LUONG",
    "THAT_SAT", "PHA_QUAN",
)  # fmt: skip


class ReviewState(StrEnum):
    PENDING = "PENDING"
    IN_REVIEW = "IN_REVIEW"
    VERIFIED = "VERIFIED"
    DISAGREEMENT = "DISAGREEMENT"
    BLOCKED = "BLOCKED"


class ComparisonStatus(StrEnum):
    MATCH = "MATCH"
    MISMATCH = "MISMATCH"
    UNVERIFIED = "UNVERIFIED"


@dataclass(frozen=True, slots=True)
class StarComparison:
    star: str
    engine: str | None
    expected: str | None
    status: ComparisonStatus

    def to_dict(self) -> dict[str, object]:
        return {
            "star": self.star,
            "engine": self.engine,
            "expected": self.expected,
            "status": self.status.value,
        }


def compare_stars(
    candidate: dict[str, str] | None, expected: dict[str, str] | None
) -> list[StarComparison]:
    """One row per major star. A missing expectation is UNVERIFIED, not a match."""
    rows: list[StarComparison] = []
    for code in MAJOR_STAR_CODES:
        engine_value = (candidate or {}).get(code)
        expected_value = (expected or {}).get(code)
        if expected_value is None:
            status = ComparisonStatus.UNVERIFIED
        elif expected_value == engine_value:
            status = ComparisonStatus.MATCH
        else:
            status = ComparisonStatus.MISMATCH
        rows.append(StarComparison(code, engine_value, expected_value, status))
    return rows


@dataclass(slots=True)
class FixtureReview:
    """What a reviewer asserts about one fixture. Never written by the engine."""

    state: ReviewState = ReviewState.PENDING
    expected_tu_vi: str | None = None
    expected_stars: dict[str, str] | None = None
    expected_tuan: list[str] | None = None
    expected_triet: list[str] | None = None
    independently_confirmed: bool = False
    reviewer: str | None = None
    reviewed_at: str | None = None
    source_id: str | None = None
    page: str | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "state": self.state.value,
            "expected_tu_vi": self.expected_tu_vi,
            "expected_stars": self.expected_stars,
            "expected_tuan": self.expected_tuan,
            "expected_triet": self.expected_triet,
            "independently_confirmed": self.independently_confirmed,
            "reviewer": self.reviewer,
            "reviewed_at": self.reviewed_at,
            "source_id": self.source_id,
            "page": self.page,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any] | None) -> FixtureReview:
        if not raw:
            return cls()
        stars = raw.get("expected_stars")
        return cls(
            state=ReviewState(str(raw.get("state", ReviewState.PENDING.value))),
            expected_tu_vi=_opt_str(raw.get("expected_tu_vi")),
            expected_stars={str(k): str(v) for k, v in stars.items()} if stars else None,
            expected_tuan=list(raw["expected_tuan"]) if raw.get("expected_tuan") else None,
            expected_triet=list(raw["expected_triet"]) if raw.get("expected_triet") else None,
            independently_confirmed=bool(raw.get("independently_confirmed", False)),
            reviewer=_opt_str(raw.get("reviewer")),
            reviewed_at=_opt_str(raw.get("reviewed_at")),
            source_id=_opt_str(raw.get("source_id")),
            page=_opt_str(raw.get("page")),
            notes=str(raw.get("notes") or ""),
        )

    @property
    def has_expected_values(self) -> bool:
        return bool(
            self.expected_tu_vi
            and self.expected_stars
            and set(self.expected_stars) == set(MAJOR_STAR_CODES)
        )


def _opt_str(value: object) -> str | None:
    return None if value is None else str(value)


@dataclass(frozen=True, slots=True)
class StateEvaluation:
    """The state a review has earned, and everything standing in its way."""

    state: ReviewState
    blockers: tuple[str, ...] = ()
    mismatches: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "state": self.state.value,
            "blockers": list(self.blockers),
            "mismatches": list(self.mismatches),
        }


def evaluate_state(
    *,
    review: FixtureReview,
    candidate: dict[str, str] | None,
    source: Source | None,
    blocked_reason: str | None = None,
) -> StateEvaluation:
    """Derive the review state. Never trusts a stored ``state`` field.

    Storing a state and trusting it would let an edit elsewhere leave a fixture
    claiming VERIFIED while its evidence has gone. The state is therefore always
    recomputed from the evidence actually present.
    """
    if blocked_reason:
        return StateEvaluation(ReviewState.BLOCKED, (blocked_reason,))

    if not review.has_expected_values:
        # "Started" means somebody began entering findings — a reviewer name or a
        # partial expectation. Notes alone do not count: a note can be a question.
        started = any((review.expected_tu_vi, review.expected_stars, review.reviewer))
        state = ReviewState.IN_REVIEW if started else ReviewState.PENDING
        return StateEvaluation(state, ("Chưa nhập đủ giá trị kỳ vọng độc lập.",))

    mismatches = tuple(
        row.star for row in compare_stars(candidate, review.expected_stars)
        if row.status is ComparisonStatus.MISMATCH
    )
    tu_vi_mismatch = (
        review.expected_tu_vi != (candidate or {}).get("TU_VI")
        if review.expected_tu_vi
        else False
    )
    if mismatches or tu_vi_mismatch:
        # A disagreement is a finding, not a failure to be tidied away. It stays
        # visible until somebody decides whether the engine or the source is wrong.
        return StateEvaluation(ReviewState.DISAGREEMENT, (), mismatches)

    # Everything agrees — which is exactly when it is easiest to accept a
    # fixture that was quietly copied from the engine. Hence the evidence gate.
    blockers: list[str] = []
    if not review.independently_confirmed:
        blockers.append(
            "Khớp hoàn toàn với engine nhưng chưa tích independently_confirmed — "
            "phải xác nhận là đã tra nguồn độc lập, không phải chép lại."
        )
    if not review.reviewer:
        blockers.append("Thiếu tên người thẩm định.")
    if not review.reviewed_at:
        blockers.append("Thiếu thời điểm thẩm định.")
    if source is None:
        blockers.append("Thiếu nguồn đối chiếu.")
    elif not source.is_citable:
        blockers.append(f"Nguồn '{source.id}' chưa đủ thông tin để người khác tra lại.")

    if blockers:
        return StateEvaluation(ReviewState.IN_REVIEW, tuple(blockers))
    return StateEvaluation(ReviewState.VERIFIED)
