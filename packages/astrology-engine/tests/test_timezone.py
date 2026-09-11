"""Timezone resolution, and why a hard-coded +7 was not good enough."""

from __future__ import annotations

import pytest

from cosmic_astrology import BirthInput, build_chart
from cosmic_astrology.calendar.lunar import solar_to_lunar
from cosmic_astrology.chart.types import CalendarType, EngineStage, Gender
from cosmic_astrology.conventions import TimezonePolicy
from cosmic_astrology.timezone import resolve_timezone, tzdata_version

HCM = "Asia/Ho_Chi_Minh"


def _resolve(year: int, *, timezone_id: str | None = HCM, hour: int = 12) -> float:
    return resolve_timezone(
        policy=TimezonePolicy.IANA_HISTORICAL,
        year=year,
        month=6,
        day=15,
        hour=hour,
        minute=0,
        timezone_id=timezone_id,
        fallback_offset=7.0,
    ).utc_offset_hours


def test_vietnam_did_not_sit_on_utc_plus_7_for_the_whole_century() -> None:
    """The reason this module exists: 1968 was not +7.

    Per the IANA database the South ran on UTC+8 from 1960 until mid-1975. A
    person born then is a living adult today, so this is not a historical
    curiosity — it is a correctness bug for real customers.
    """
    assert _resolve(1968) == 8.0
    assert _resolve(1990) == 7.0
    assert _resolve(2020) == 7.0


def test_the_offset_is_read_at_the_birth_instant_not_at_run_time() -> None:
    assert _resolve(1968) != _resolve(1990)


def test_a_resolved_offset_says_where_it_came_from() -> None:
    resolution = resolve_timezone(
        policy=TimezonePolicy.IANA_HISTORICAL,
        year=1968, month=6, day=15, hour=12, minute=0,
        timezone_id=HCM, fallback_offset=7.0,
    )
    assert resolution.resolved_from_database is True
    assert HCM in resolution.source
    assert "tzdata" in resolution.source or "tzdb" in resolution.source


def test_without_a_zone_id_the_chart_does_not_claim_a_database_lookup() -> None:
    """Honesty about provenance: a caller-supplied offset must not look resolved."""
    resolution = resolve_timezone(
        policy=TimezonePolicy.IANA_HISTORICAL,
        year=1968, month=6, day=15, hour=12, minute=0,
        timezone_id=None, fallback_offset=7.0,
    )
    assert resolution.resolved_from_database is False
    assert resolution.policy is TimezonePolicy.FIXED_OFFSET
    assert resolution.utc_offset_hours == 7.0


def test_an_unknown_zone_is_rejected_rather_than_defaulted() -> None:
    with pytest.raises(ValueError, match="Không tìm thấy múi giờ"):
        resolve_timezone(
            policy=TimezonePolicy.IANA_HISTORICAL,
            year=1990, month=1, day=1, hour=12, minute=0,
            timezone_id="Asia/Nowhere", fallback_offset=7.0,
        )


def test_the_wrong_offset_really_does_change_the_lunar_date() -> None:
    """Proof the hour matters, not just the metadata.

    14 May 1961 lands on a different lunar month depending on the offset — so a
    chart built with the hard-coded +7 would have been wrong for that birth.
    """
    with_seven = solar_to_lunar(14, 5, 1961, 7.0)
    with_eight = solar_to_lunar(14, 5, 1961, 8.0)
    assert (with_seven.day, with_seven.month) != (with_eight.day, with_eight.month)


def test_a_historical_birth_resolves_through_the_database_end_to_end() -> None:
    birth = BirthInput(
        name="x", gender=Gender.MALE, calendar_type=CalendarType.SOLAR,
        day=14, month=5, year=1961, hour=8, timezone_id=HCM,
    )
    chart = build_chart(birth, stage=EngineStage.PREVIEW).to_dict()
    assert chart["timezone"]["utc_offset_hours"] == 8.0
    assert chart["timezone"]["resolved_from_database"] is True
    assert chart["birth"]["tz_offset"] == 8.0


def test_the_tz_database_version_is_recorded() -> None:
    """Two machines must not silently disagree about 1968."""
    assert tzdata_version()
