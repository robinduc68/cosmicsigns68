"""Verification workbench: the model behind independent review of the engine.

Nothing here calculates astrology. It holds what a *reviewer* asserts, keeps
that strictly apart from what the engine computed, and refuses to let the two be
confused — which is the only reason the fixture matrix is worth anything.
"""

from cosmic_astrology.review.discrepancy import Discrepancy, DiscrepancyStatus
from cosmic_astrology.review.model import (
    MAJOR_STAR_CODES,
    ComparisonStatus,
    FixtureReview,
    ReviewState,
    StarComparison,
    StateEvaluation,
    compare_stars,
    evaluate_state,
)
from cosmic_astrology.review.pack import (
    ImportOutcome,
    apply_import,
    export_csv,
    export_json,
    preview_import,
)
from cosmic_astrology.review.promotion import PromotionResult, promote_rule_verification
from cosmic_astrology.review.sources import Source, SourceRegistry, SourceType
from cosmic_astrology.review.store import FixtureRecord, ReviewStore, load_store

__all__ = [
    "MAJOR_STAR_CODES",
    "ComparisonStatus",
    "Discrepancy",
    "DiscrepancyStatus",
    "FixtureRecord",
    "FixtureReview",
    "ImportOutcome",
    "PromotionResult",
    "ReviewState",
    "ReviewStore",
    "Source",
    "SourceRegistry",
    "SourceType",
    "StarComparison",
    "StateEvaluation",
    "apply_import",
    "compare_stars",
    "evaluate_state",
    "export_csv",
    "export_json",
    "load_store",
    "preview_import",
    "promote_rule_verification",
]
