"""Star metadata — what a star *is*, separate from where it lands.

Placement lives in ``chart.builder``. This package answers the other question:
a star's identity, ngũ hành, âm/dương and category, none of which depend on a
birth moment.
"""

from cosmic_astrology.stars.catalog import (
    STAR_CATALOG,
    BlankReason,
    CategoryCoverage,
    MetadataCoverage,
    Polarity,
    StarDefinition,
    canonical_form,
    definition_for,
    metadata_coverage,
)

__all__ = [
    "STAR_CATALOG",
    "BlankReason",
    "CategoryCoverage",
    "MetadataCoverage",
    "Polarity",
    "StarDefinition",
    "canonical_form",
    "definition_for",
    "metadata_coverage",
]
