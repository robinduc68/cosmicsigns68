"""Cosmic Astrology — deterministic calculation layer for Cosmic Signs.

This package is the *CALCULATION* layer described in ``docs/architecture.md``.
It must never call an LLM, never perform I/O and never produce random output:
the same input always yields the same output.

Every school-dependent rule is selected by a :class:`ConventionProfile` rather
than being buried in calculation code, and the profile's id and version are
stamped into every chart. See ``docs/astrology-conventions.md``.
"""

from cosmic_astrology.birth_moment import ResolvedBirthDates, resolve_birth_dates
from cosmic_astrology.calendar.lunar import LunarDate, lunar_to_solar, solar_to_lunar
from cosmic_astrology.calendar.sexagenary import (
    SexagenaryPillars,
    hour_branch_index,
    pillars_for_birth,
)
from cosmic_astrology.chart.builder import ENGINE_VERSION, build_chart
from cosmic_astrology.chart.types import BirthInput, Chart, EngineStage
from cosmic_astrology.conventions import (
    COSMIC_SIGNS_STANDARD_V1,
    ConventionProfile,
    LateZiPolicy,
    RuleId,
    TimezonePolicy,
    UnresolvedConventionError,
    VerificationStatus,
    is_production_ready,
    needs_recalculation,
    validate_convention_profile,
)
from cosmic_astrology.timezone import TimezoneResolution, resolve_timezone
from cosmic_astrology.trace import TraceLog

__all__ = [
    "COSMIC_SIGNS_STANDARD_V1",
    "ENGINE_VERSION",
    "BirthInput",
    "Chart",
    "ConventionProfile",
    "EngineStage",
    "LateZiPolicy",
    "LunarDate",
    "ResolvedBirthDates",
    "RuleId",
    "SexagenaryPillars",
    "TimezonePolicy",
    "TimezoneResolution",
    "TraceLog",
    "UnresolvedConventionError",
    "VerificationStatus",
    "build_chart",
    "hour_branch_index",
    "is_production_ready",
    "lunar_to_solar",
    "needs_recalculation",
    "pillars_for_birth",
    "resolve_birth_dates",
    "resolve_timezone",
    "solar_to_lunar",
    "validate_convention_profile",
]

__version__ = "0.2.0"
