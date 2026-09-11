from __future__ import annotations

import pytest

from cosmic_astrology.calendar.sexagenary import (
    Element,
    hour_branch_index,
    nap_am_element,
    pillars_for_birth,
    sexagenary_index,
    year_pillar,
)


@pytest.mark.parametrize(
    ("year", "expected"),
    [(1984, "Giáp Tý"), (1992, "Nhâm Thân"), (2000, "Canh Thìn"), (2026, "Bính Ngọ")],
)
def test_year_pillar(year: int, expected: str) -> None:
    assert year_pillar(year).name == expected


@pytest.mark.parametrize(
    ("hour", "expected"),
    [(23, 0), (0, 0), (1, 1), (2, 1), (11, 6), (12, 6), (14, 7), (22, 11)],
)
def test_hour_branch_index(hour: int, expected: int) -> None:
    assert hour_branch_index(hour) == expected


def test_hour_branch_rejects_out_of_range() -> None:
    with pytest.raises(ValueError):
        hour_branch_index(24)


def test_nap_am_of_known_pillars() -> None:
    assert nap_am_element(0, 0) == ("Hải Trung Kim", Element.KIM)  # Giáp Tý
    assert nap_am_element(8, 8) == ("Kiếm Phong Kim", Element.KIM)  # Nhâm Thân
    assert nap_am_element(8, 2)[1] is Element.KIM  # Nhâm Dần — Kim Bạch Kim


def test_sexagenary_index_covers_the_cycle() -> None:
    seen = {sexagenary_index(i % 10, i % 12) for i in range(60)}
    assert seen == set(range(60))


def test_pillars_for_a_known_birth() -> None:
    pillars = pillars_for_birth(10, 9, 1992, 14, day_pillar_solar=(10, 9, 1992))
    assert pillars.year.name == "Nhâm Thân"
    assert pillars.month.chi == "Dậu"  # lunar month 8 → Dậu
    assert pillars.hour.chi == "Mùi"


def test_the_day_pillar_follows_the_date_it_is_given_not_the_hour() -> None:
    """Deciding whether 23:xx rolls over is a convention choice, not this function's.

    It used to be made here, silently and in the opposite direction from
    ``build_chart``. Now the caller passes the date and this function obeys.
    """
    same_day = pillars_for_birth(10, 9, 1992, 23, day_pillar_solar=(10, 9, 1992))
    next_day = pillars_for_birth(10, 9, 1992, 23, day_pillar_solar=(11, 9, 1992))

    assert same_day.hour.chi == "Tý"
    assert next_day.hour.chi == "Tý"
    assert next_day.day.can_index == (same_day.day.can_index + 1) % 10
