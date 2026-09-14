"""Bất biến của phụ tinh nhóm 1.

Bốn hệ quả dưới đây **suy thẳng từ luật**, nên chúng bắt được lỗi bảng mà không cần
chờ nguồn ngoài — đúng loại kiểm tra dùng được trong lúc mọi thứ còn PROVISIONAL.

Có một bất biến ở đây tồn tại vì một khẳng định **sai** của chính người viết: bản
đầu ghi "Văn Xương và Văn Khúc luôn đối cung". Chúng không đối cung; chúng đối xứng
qua trục Thìn–Tuất và **đồng cung tại Sửu/Mùi**. Rút gọn `place_van_khuc` thành
`place_van_xuong(h) + 6` là cách tái phát lỗi đó trong một dòng.
"""

from __future__ import annotations

import pytest

from cosmic_astrology.calendar.sexagenary import CAN, CHI
from cosmic_astrology.stars import placement

TU_CHINH = {"Tý", "Ngọ", "Mão", "Dậu"}
TU_SINH = {"Dần", "Thân", "Tỵ", "Hợi"}
TU_MO = {"Thìn", "Tuất", "Sửu", "Mùi"}


def test_van_xuong_and_van_khuc_share_a_palace_at_suu_and_mui() -> None:
    together = {
        CHI[placement.place_van_xuong(h)]
        for h in range(12)
        if placement.place_van_xuong(h) == placement.place_van_khuc(h)
    }
    assert together == {"Sửu", "Mùi"}
    # Và chúng KHÔNG đối cung — chỉ trùng khớp ở giờ Tý và giờ Ngọ.
    opposite = [
        h
        for h in range(12)
        if (placement.place_van_xuong(h) - placement.place_van_khuc(h)) % 12 == 6
    ]
    assert [CHI[h] for h in opposite] == ["Tý", "Ngọ"]


@pytest.mark.parametrize("year_branch", range(12))
def test_dao_hoa_always_lands_on_a_cardinal_branch(year_branch: int) -> None:
    assert CHI[placement.place_dao_hoa(year_branch)] in TU_CHINH


@pytest.mark.parametrize("year_branch", range(12))
def test_thien_ma_always_lands_on_a_growth_branch(year_branch: int) -> None:
    assert CHI[placement.place_thien_ma(year_branch)] in TU_SINH


@pytest.mark.parametrize("year_branch", range(12))
def test_hong_loan_and_thien_hy_are_opposite(year_branch: int) -> None:
    hong_loan = placement.place_hong_loan(year_branch)
    thien_hy = placement.place_thien_hy(year_branch)
    assert (hong_loan - thien_hy) % 12 == 6


@pytest.mark.parametrize("year_stem", range(10))
def test_kinh_duong_and_da_la_straddle_loc_ton(year_stem: int) -> None:
    loc_ton = placement.place_loc_ton(year_stem)
    assert placement.place_kinh_duong(loc_ton) == (loc_ton + 1) % 12
    assert placement.place_da_la(loc_ton) == (loc_ton - 1) % 12
    assert CHI[loc_ton] not in TU_MO, f"Lộc Tồn không vào tứ mộ (can {CAN[year_stem]})"


def test_the_whole_group_lands_on_a_real_branch() -> None:
    """Một hàm trả về ngoài 0–11 sẽ làm hỏng cung một cách âm thầm."""
    for hour in range(12):
        assert 0 <= placement.place_van_xuong(hour) <= 11
        assert 0 <= placement.place_van_khuc(hour) <= 11
    for month in range(1, 13):
        assert 0 <= placement.place_ta_phu(month) <= 11
        assert 0 <= placement.place_huu_bat(month) <= 11
    for stem in range(10):
        assert 0 <= placement.place_thien_khoi(stem) <= 11
        assert 0 <= placement.place_thien_viet(stem) <= 11


def test_out_of_range_input_is_rejected_rather_than_wrapped() -> None:
    """Tháng 13 hay giờ 12 là lỗi gọi hàm; im lặng mod 12 sẽ giấu nó đi."""
    with pytest.raises(ValueError):
        placement.place_van_xuong(12)
    with pytest.raises(ValueError):
        placement.place_ta_phu(13)
    with pytest.raises(ValueError):
        placement.place_thien_khoi(10)
