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
    # Thân = Mệnh + 2 × chi giờ. Giờ Mùi (7) → +14 ≡ +2 → cung thứ hai theo chiều thuận
    # từ Mệnh, tức Phúc Đức. (Giá trị cũ "Phu Thê" được sinh ra từ chính engine lỗi.)
    assert chart.than["resides_in"] == PalaceName.PHUC_DUC.value
    assert chart.cuc["number"] == 4
    assert chart.cuc["label"] == "Kim Tứ Cục"
    assert chart.yin_yang["label"] == "Dương Nam"


def test_palace_stems_follow_ngu_ho_don_across_all_twelve_palaces() -> None:
    """Năm Nhâm: tháng Giêng Nhâm Dần, rồi can đi tiếp qua đủ 12 tháng.

    Kỳ vọng suy thẳng từ định nghĩa ngũ hổ độn, không lấy từ engine. Tý và Sửu là
    tháng 11 và tháng Chạp — chúng tiếp nối sau Hợi chứ không lùi về trước Dần.
    Test cũ chỉ kiểm cung Dần nên để lọt đúng hai cung này.
    """
    expected = {
        "Dần": "Nhâm", "Mão": "Quý", "Thìn": "Giáp", "Tỵ": "Ất", "Ngọ": "Bính", "Mùi": "Đinh",
        "Thân": "Mậu", "Dậu": "Kỷ", "Tuất": "Canh", "Hợi": "Tân", "Tý": "Nhâm", "Sửu": "Quý",
    }  # fmt: skip
    chart = build_chart(_birth())
    assert {p.branch: p.stem for p in chart.palaces} == expected


def test_palace_names_run_counter_clockwise_from_menh_in_classical_order() -> None:
    """Mệnh → Huynh Đệ → Phu Thê … đi nghịch (địa chi giảm dần).

    Suy từ định nghĩa với Mệnh tại Dần. Trước bản sửa, engine đặt ngược chiều nên 10
    trong 12 tên cung sai; chỉ Mệnh và Thiên Di (đối xứng qua tâm) trùng khớp.
    """
    expected = {
        "Dần": "Mệnh", "Sửu": "Huynh Đệ", "Tý": "Phu Thê", "Hợi": "Tử Tức",
        "Tuất": "Tài Bạch", "Dậu": "Tật Ách", "Thân": "Thiên Di", "Mùi": "Nô Bộc",
        "Ngọ": "Quan Lộc", "Tỵ": "Điền Trạch", "Thìn": "Phúc Đức", "Mão": "Phụ Mẫu",
    }  # fmt: skip
    chart = build_chart(_birth())
    assert chart.menh["branch"] == "Dần"
    assert {p.branch: p.label for p in chart.palaces} == expected


def test_cross_check_against_a_third_party_reference_chart() -> None:
    """Đối chiếu chéo với một lá số in từ website bên thứ ba (lá số #139602).

    Đây là CROSS_CHECK, không phải nguồn chuẩn: nó không chứng minh engine đúng, nhưng
    chính ca này đã làm lộ hai lỗi can cung và tên cung. Giữ lại để lỗi không quay lại.
    Âm nữ, 04/03/2001 dương lịch (10/02 âm) lúc 09:30.
    """
    chart = build_chart(
        BirthInput(
            name="cross-check",
            gender=Gender.FEMALE,
            calendar_type=CalendarType.SOLAR,
            day=4,
            month=3,
            year=2001,
            hour=9,
            minute=30,
        ),
        stage=EngineStage.PREVIEW,
    )
    stems = {p.branch: p.stem for p in chart.palaces}
    names = {p.branch: p.label for p in chart.palaces}
    stars = {s.id: p.branch for p in chart.palaces for s in p.major_stars}

    assert stems == {
        "Tý": "Canh", "Sửu": "Tân", "Dần": "Canh", "Mão": "Tân", "Thìn": "Nhâm", "Tỵ": "Quý",
        "Ngọ": "Giáp", "Mùi": "Ất", "Thân": "Bính", "Dậu": "Đinh", "Tuất": "Mậu", "Hợi": "Kỷ",
    }  # fmt: skip
    assert names == {
        "Tuất": "Mệnh", "Hợi": "Phụ Mẫu", "Tý": "Phúc Đức", "Sửu": "Điền Trạch",
        "Dần": "Quan Lộc", "Mão": "Nô Bộc", "Thìn": "Thiên Di", "Tỵ": "Tật Ách",
        "Ngọ": "Tài Bạch", "Mùi": "Tử Tức", "Thân": "Phu Thê", "Dậu": "Huynh Đệ",
    }  # fmt: skip
    assert chart.than["resides_in_label"] == "Phu Thê"
    assert chart.cuc["label"] == "Mộc Tam Cục"
    assert stars == {
        "TU_VI": "Mùi", "THIEN_CO": "Ngọ", "THAI_DUONG": "Thìn", "VU_KHUC": "Mão",
        "THIEN_DONG": "Dần", "LIEM_TRINH": "Hợi", "THIEN_PHU": "Dậu", "THAI_AM": "Tuất",
        "THAM_LANG": "Hợi", "CU_MON": "Tý", "THIEN_TUONG": "Sửu", "THIEN_LUONG": "Dần",
        "THAT_SAT": "Mão", "PHA_QUAN": "Mùi",
    }  # fmt: skip


def test_than_can_only_reside_in_the_six_classical_palaces() -> None:
    """Thân − Mệnh luôn là số chẵn, nên Thân chỉ cư được đúng sáu cung."""
    allowed = {"Mệnh", "Phúc Đức", "Quan Lộc", "Thiên Di", "Tài Bạch", "Phu Thê"}
    seen = set()
    for hour in range(0, 23, 2):
        chart = build_chart(_birth(hour=hour))
        seen.add(chart.than["resides_in_label"])
    assert seen == allowed


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
    # Nam phái an cả phụ tinh nhóm 1, nên lọc riêng chính tinh.
    stars = [s for p in chart.palaces for s in p.major_stars]
    assert len(stars) == 14
    assert {s.id for s in stars} == {
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
