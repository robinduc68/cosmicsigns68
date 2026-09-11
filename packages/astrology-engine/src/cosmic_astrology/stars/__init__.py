"""Star metadata — what a star *is*, separate from where it lands.

Placement lives in ``chart.builder``. This package answers the other question:
a star's ngũ hành and âm/dương, which are properties of the star itself and do
not depend on a birth moment.
"""

from cosmic_astrology.stars.metadata import (
    STAR_METADATA,
    ElementCoverage,
    Polarity,
    StarMetadata,
    element_coverage,
    metadata_for,
)

__all__ = [
    "STAR_METADATA",
    "ElementCoverage",
    "Polarity",
    "StarMetadata",
    "element_coverage",
    "metadata_for",
]
