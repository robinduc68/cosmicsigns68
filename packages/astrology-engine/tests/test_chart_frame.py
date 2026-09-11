from __future__ import annotations

import pytest

from cosmic_astrology.chart.builder import build_chart, three_directions_four_positions
from cosmic_astrology.chart.types import (
    BirthInput,
    CalendarType,
    EngineStage,
    Gender,
    PalaceName,
)


def _birth(**overrides: object) -> BirthInput:
    defaults: dict[str, object] = {
        "name": "Người dùng thử",
        "gender": Gender.MALE,
        "calendar_type": CalendarType.SOLAR,
        "day": 10,
        "month": 9,
        "year": 1992,
        "hour": 14,
    }
    defaults.update(overrides)
    return BirthInput(**defaults)  # type: ignore[arg-type]


def test_chart_has_twelve_unique_palaces() -> None:
    chart = build_chart(_birth())
    branches = [p.branch_index for p in chart.palaces]
    assert len(chart.palaces) == 12
    assert sorted(branches) == list(range(12))
    assert {p.name for p in chart.palaces} == set(PalaceName)


def test_menh_than_and_cuc_for_a_known_birth() -> None:
    chart = build_chart(_birth())
    assert chart.menh["branch"] == "Dần"
    assert chart.than["branch"] == "Thìn"
    assert chart.than["resides_in"] == PalaceName.PHU_THE.value
    assert chart.cuc["number"] == 4
    assert chart.cuc["label"] == "Kim Tứ Cục"
    assert chart.yin_yang["label"] == "Dương Nam"


def test_palace_stems_follow_ngu_ho_don() -> None:
    chart = build_chart(_birth())
    dan = next(p for p in chart.palaces if p.branch == "Dần")
    assert dan.stem == "Nhâm"  # năm Nhâm → tháng Giêng Nhâm Dần


def test_tuan_and_triet_are_placed_on_two_palaces_each() -> None:
    chart = build_chart(_birth())
    assert sum(p.has_tuan for p in chart.palaces) == 2
    assert sum(p.has_triet for p in chart.palaces) == 2
    assert {p.branch for p in chart.palaces if p.has_triet} == {"Dần", "Mão"}
    assert {p.branch for p in chart.palaces if p.has_tuan} == {"Tuất", "Hợi"}


def test_lunar_input_produces_the_same_chart_as_the_matching_solar_input() -> None:
    solar_chart = build_chart(_birth())
    lunar_chart = build_chart(_birth(calendar_type=CalendarType.LUNAR, day=14, month=8, year=1992))
    assert lunar_chart.menh == solar_chart.menh
    assert lunar_chart.cuc == solar_chart.cuc


def test_frame_stage_places_no_stars() -> None:
    chart = build_chart(_birth(), stage=EngineStage.FRAME)
    assert all(not p.stars for p in chart.palaces)
    assert chart.to_dict()["engine"] == {
        "stage": "FRAME",
        "version": chart.engine_version,
        "is_authoritative": False,
        "convention_profile": chart.convention_profile,
        "convention_version": chart.convention_version,
    }


def test_preview_stage_places_all_fourteen_major_stars_and_marks_them_provisional() -> None:
    chart = build_chart(_birth(), stage=EngineStage.PREVIEW)
    stars = [s for p in chart.palaces for s in p.stars]
    assert len(stars) == 14
    assert {s.code for s in stars} == {
        "TU_VI", "THIEN_CO", "THAI_DUONG", "VU_KHUC", "THIEN_DONG", "LIEM_TRINH",
        "THIEN_PHU", "THAI_AM", "THAM_LANG", "CU_MON", "THIEN_TUONG", "THIEN_LUONG",
        "THAT_SAT", "PHA_QUAN",
    }  # fmt: skip
    assert all(s.provisional for s in stars)


def test_vo_chinh_dieu_is_flagged() -> None:
    chart = build_chart(_birth(), stage=EngineStage.PREVIEW)
    empty = [p for p in chart.palaces if p.is_empty_main_star]
    assert empty, "một lá số luôn có ít nhất một cung vô chính diệu"


def test_full_stage_is_not_available_yet() -> None:
    with pytest.raises(NotImplementedError):
        build_chart(_birth(), stage=EngineStage.FULL)


def test_three_directions_four_positions() -> None:
    assert three_directions_four_positions(2) == {
        "self": 2,
        "trine_left": 6,
        "trine_right": 10,
        "opposite": 8,
    }


@pytest.mark.parametrize(
    ("field", "value"),
    [("month", 13), ("day", 0), ("year", 1899), ("hour", 24), ("minute", 60)],
)
def test_birth_input_validation(field: str, value: int) -> None:
    with pytest.raises(ValueError):
        _birth(**{field: value})


def test_building_the_same_chart_twice_is_deterministic() -> None:
    first = build_chart(_birth(), stage=EngineStage.PREVIEW).to_dict()
    second = build_chart(_birth(), stage=EngineStage.PREVIEW).to_dict()
    assert first == second
