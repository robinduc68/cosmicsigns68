"""Reading and writing the verification matrix.

The matrix file is the boundary between two kinds of data that must never merge:
what the engine computed (``engine_candidate_stars``) and what a reviewer found
in a source (``review.expected_*``). Every write path here refuses to let the
second be filled in from the first.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from cosmic_astrology.review.discrepancy import Discrepancy
from cosmic_astrology.review.model import (
    FixtureReview,
    ReviewState,
    StateEvaluation,
    compare_stars,
    evaluate_state,
)
from cosmic_astrology.review.sources import Source, SourceRegistry

__all__ = ["FixtureRecord", "ReviewStore", "load_store"]

_ENGINE_ROOT = Path(__file__).resolve().parents[3]
MATRIX_PATH = _ENGINE_ROOT / "tests" / "fixtures" / "major_stars_matrix.json"
SOURCES_PATH = _ENGINE_ROOT / "tests" / "fixtures" / "sources.json"


@dataclass(slots=True)
class FixtureRecord:
    """One verification case: engine side, reviewer side, kept apart."""

    raw: dict[str, Any]
    review: FixtureReview

    @property
    def id(self) -> str:
        return str(self.raw["id"])

    @property
    def candidate(self) -> dict[str, str] | None:
        return self.raw.get("engine_candidate_stars")

    @property
    def blocked_reason(self) -> str | None:
        return self.raw.get("blocked")

    def evaluate(self, registry: SourceRegistry) -> StateEvaluation:
        return evaluate_state(
            review=self.review,
            candidate=self.candidate,
            source=registry.get(self.review.source_id),
            blocked_reason=self.blocked_reason,
        )

    def comparisons(self) -> list[dict[str, object]]:
        return [c.to_dict() for c in compare_stars(self.candidate, self.review.expected_stars)]


@dataclass(slots=True)
class ReviewStore:
    matrix_path: Path
    sources_path: Path
    data: dict[str, Any]
    registry: SourceRegistry
    discrepancies: list[Discrepancy] = field(default_factory=list)

    # ---------------------------------------------------------------- reading

    @property
    def records(self) -> list[FixtureRecord]:
        return [
            FixtureRecord(raw=case, review=FixtureReview.from_dict(case.get("review")))
            for case in self.data["cases"]
        ]

    def record(self, fixture_id: str) -> FixtureRecord:
        for rec in self.records:
            if rec.id == fixture_id:
                return rec
        raise KeyError(f"Không có fixture '{fixture_id}'")

    def states(self) -> dict[str, StateEvaluation]:
        return {rec.id: rec.evaluate(self.registry) for rec in self.records}

    def summary(self) -> dict[str, int]:
        counts = dict.fromkeys((s.value for s in ReviewState), 0)
        for evaluation in self.states().values():
            counts[evaluation.state.value] += 1
        counts["TOTAL"] = len(self.data["cases"])
        return counts

    # ---------------------------------------------------------------- writing

    def save_review(self, fixture_id: str, review: FixtureReview) -> StateEvaluation:
        """Store reviewer input. The candidate block is never touched."""
        for case in self.data["cases"]:
            if case["id"] == fixture_id:
                case["review"] = review.to_dict()
                record = FixtureRecord(raw=case, review=review)
                evaluation = record.evaluate(self.registry)
                # The stored state is a cached read of the evidence, recomputed on
                # every load — it is never the thing that decides.
                case["review"]["state"] = evaluation.state.value
                self._write()
                return evaluation
        raise KeyError(f"Không có fixture '{fixture_id}'")

    def add_discrepancy(self, discrepancy: Discrepancy) -> None:
        self.discrepancies.append(discrepancy)
        self.data["discrepancies"] = [d.to_dict() for d in self.discrepancies]
        self._write()

    def add_source(self, source: Source) -> None:
        self.registry.add(source)
        self.sources_path.write_text(
            json.dumps(self.registry.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def _write(self) -> None:
        self.matrix_path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )


def load_store(
    matrix_path: Path = MATRIX_PATH, sources_path: Path = SOURCES_PATH
) -> ReviewStore:
    data = json.loads(matrix_path.read_text(encoding="utf-8"))
    registry = (
        SourceRegistry.from_dict(json.loads(sources_path.read_text(encoding="utf-8")))
        if sources_path.exists()
        else SourceRegistry()
    )
    discrepancies = [Discrepancy.from_dict(d) for d in data.get("discrepancies", [])]
    return ReviewStore(
        matrix_path=matrix_path,
        sources_path=sources_path,
        data=data,
        registry=registry,
        discrepancies=discrepancies,
    )
