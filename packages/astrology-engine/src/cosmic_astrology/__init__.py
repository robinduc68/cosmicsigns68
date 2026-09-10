"""Cosmic Astrology — deterministic calculation layer for Cosmic Signs.

This package is the *CALCULATION* layer described in ``docs/architecture.md``.
It must never call an LLM, never perform I/O and never produce random output:
the same input always yields the same output.
"""

from cosmic_astrology.calendar.lunar import LunarDate, lunar_to_solar, solar_to_lunar
from cosmic_astrology.calendar.sexagenary import (
    SexagenaryPillars,
    hour_branch_index,
    pillars_for_birth,
)
from cosmic_astrology.chart.builder import build_chart
from cosmic_astrology.chart.types import BirthInput, Chart, EngineStage

__all__ = [
    "BirthInput",
    "Chart",
    "EngineStage",
    "LunarDate",
    "SexagenaryPillars",
    "build_chart",
    "hour_branch_index",
    "lunar_to_solar",
    "pillars_for_birth",
    "solar_to_lunar",
]

__version__ = "0.1.0"
