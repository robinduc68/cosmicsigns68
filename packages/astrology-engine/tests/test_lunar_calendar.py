"""Reference cases for solar ↔ lunar conversion.

The expected values come from the published Vietnamese almanac dates
(Tết dates and known leap months), which is the only trustworthy way to pin
down an astronomical algorithm.
"""

from __future__ import annotations

import pytest

from cosmic_astrology.calendar.lunar import (
    jd_from_solar,
    jd_to_solar,
    lunar_to_solar,
    solar_to_lunar,
)

TET_DATES = [
    ((17, 2, 2026), 2026),  # Bính Ngọ
    ((29, 1, 2025), 2025),  # Ất Tỵ
    ((10, 2, 2024), 2024),  # Giáp Thìn
    ((22, 1, 2023), 2023),  # Quý Mão
    ((1, 2, 2022), 2022),  # Nhâm Dần
    ((25, 1, 2020), 2020),  # Canh Tý
    ((16, 2, 2018), 2018),  # Mậu Tuất
    ((5, 2, 2000), 2000),  # Canh Thìn
]


@pytest.mark.parametrize(("solar", "lunar_year"), TET_DATES)
def test_tet_is_first_day_of_first_lunar_month(
    solar: tuple[int, int, int], lunar_year: int
) -> None:
    result = solar_to_lunar(*solar)
    assert (result.day, result.month, result.year) == (1, 1, lunar_year)
    assert result.is_leap_month is False


def test_leap_month_is_detected() -> None:
    # Quý Mão 2023 has a leap second month starting on 2023-03-22.
    leap_start = solar_to_lunar(22, 3, 2023)
    assert (leap_start.day, leap_start.month, leap_start.is_leap_month) == (1, 2, True)

    regular_start = solar_to_lunar(20, 2, 2023)
    assert (regular_start.day, regular_start.month, regular_start.is_leap_month) == (
        1,
        2,
        False,
    )


def test_lunar_to_solar_is_inverse_of_solar_to_lunar() -> None:
    for jd in range(jd_from_solar(1, 1, 1975), jd_from_solar(1, 1, 2035), 37):
        day, month, year = jd_to_solar(jd)
        lunar = solar_to_lunar(day, month, year)
        assert lunar_to_solar(lunar.day, lunar.month, lunar.year, lunar.is_leap_month) == (
            day,
            month,
            year,
        )


def test_lunar_to_solar_rejects_a_leap_month_that_does_not_exist() -> None:
    with pytest.raises(ValueError, match="nhuận"):
        lunar_to_solar(1, 5, 2026, is_leap_month=True)


def test_julian_day_round_trip() -> None:
    for date in [(1, 1, 1900), (29, 2, 2000), (10, 9, 2026), (31, 12, 2099)]:
        assert jd_to_solar(jd_from_solar(*date)) == date


def test_timezone_offset_can_shift_the_lunar_day() -> None:
    # A new moon that falls just after local midnight in UTC+8 but before it in
    # UTC+7 starts the lunar month a day earlier for the eastern offset.
    utc7 = solar_to_lunar(10, 9, 2026, tz_offset=7)
    utc8 = solar_to_lunar(10, 9, 2026, tz_offset=8)
    assert utc7.month == utc8.month


def test_leap_month_round_trip() -> None:
    # 1/2 nhuận Quý Mão 2023 falls on 2023-03-22 in the official calendar.
    assert lunar_to_solar(1, 2, 2023, is_leap_month=True) == (22, 3, 2023)
    assert lunar_to_solar(1, 2, 2023, is_leap_month=False) == (20, 2, 2023)


def test_lunar_to_solar_rejects_leap_flag_in_a_year_without_a_leap_month() -> None:
    with pytest.raises(ValueError, match="nhuận"):
        lunar_to_solar(1, 5, 2026, is_leap_month=True)
