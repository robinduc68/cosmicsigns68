"""Bốn sao vừa gỡ chặn, và hai nhãn Chủ Mệnh / Chủ Thân.

Bốn sao này từng bị dự án để trống có chủ ý, mỗi sao một lý do khác nhau. Ba trong
bốn lý do đã gỡ được; lý do thứ tư (Giải Thần) thì **chưa**, và sao vẫn được an —
xem ghi chú trong ``GiaiThanPolicy``. Vì vậy các bài dưới đây không khẳng định giá
trị nào là *đúng*; chúng canh những thứ **suy được từ chính luật**, để một ô gõ sai
lộ ra mà không cần chờ ai đối chiếu ấn bản.
"""

from __future__ import annotations

import pytest

from cosmic_astrology.calendar.sexagenary import CAN, CHI
from cosmic_astrology.stars import placement_group2 as group2
from cosmic_astrology.stars import placement_group3 as group3
from cosmic_astrology.stars.rulers import (
    CHU_MENH_BY_YEAR_BRANCH,
    CHU_THAN_BY_YEAR_BRANCH,
    rulers_for_year_branch,
)


def test_chu_menh_doi_xung_qua_truc_ty_ngo() -> None:
    """Chủ Mệnh soi gương qua trục Tý–Ngọ: Sửu↔Hợi, Dần↔Tuất, Thìn↔Thân…

    Không có công thức nào sinh ra bảng này, nên thứ bắt được lỗi chép là cấu trúc.
    """
    assert len(CHU_MENH_BY_YEAR_BRANCH) == 12
    for i in range(1, 12):
        if i == 6:
            continue
        assert CHU_MENH_BY_YEAR_BRANCH[i] == CHU_MENH_BY_YEAR_BRANCH[12 - i], CHI[i]


def test_chu_than_doi_xung_theo_truc_xung_chieu() -> None:
    """Chủ Thân soi theo **cung xung chiếu** (i ↔ i+6), không theo trục Tý–Ngọ.

    Hai bảng có hai kiểu đối xứng khác nhau, và đó không phải nhầm lẫn: Sửu↔Mùi,
    Dần↔Thân, Mão↔Dậu, Thìn↔Tuất, Tỵ↔Hợi đều là các cặp đối cung.

    Ngoại lệ **duy nhất** là cặp Tý/Ngọ — Linh Tinh và Hỏa Tinh. Ghi thẳng ngoại lệ
    ra đây thay vì nới lỏng bài kiểm: một ngoại lệ được nêu tên thì vẫn canh được,
    một bài kiểm bị nới lỏng thì không.
    """
    assert len(CHU_THAN_BY_YEAR_BRANCH) == 12
    for i in range(1, 6):
        assert CHU_THAN_BY_YEAR_BRANCH[i] == CHU_THAN_BY_YEAR_BRANCH[i + 6], CHI[i]
    assert CHU_THAN_BY_YEAR_BRANCH[0] == "Linh Tinh"
    assert CHU_THAN_BY_YEAR_BRANCH[6] == "Hỏa Tinh"


def test_chu_menh_chu_than_khong_phai_sao_an_vao_cung() -> None:
    """Chốt chặn cái sai dễ xảy ra nhất: đẩy hai nhãn này vào ``palace.stars``.

    Chúng là nhãn ở khối giữa. Nếu ai đó an chúng như sao, lá số sẽ hiện hai lần
    cùng một ngôi sao và mọi phép đếm sai theo.
    """
    from cosmic_astrology import BirthInput, build_chart
    from cosmic_astrology.chart.types import CalendarType, EngineStage, Gender

    chart = build_chart(
        BirthInput(
            name="x",
            gender=Gender.MALE,
            calendar_type=CalendarType.SOLAR,
            day=13,
            month=10,
            year=1999,
            hour=12,
            minute=30,
            timezone_id="Asia/Ho_Chi_Minh",
        ),
        stage=EngineStage.PREVIEW,
    )
    assert chart.traditional.chu_menh == "Văn Khúc"
    assert chart.traditional.chu_than == "Thiên Đồng"
    assert rulers_for_year_branch(CHI.index("Mão")) == ("Văn Khúc", "Thiên Đồng")

    ids = [star.id for star in chart.stars]
    assert len(ids) == len(set(ids)), "một ngôi sao chỉ được an đúng một lần"


@pytest.mark.parametrize("stem", range(10))
def test_luu_ha_va_thien_tru_phu_kin_ca_muoi_can(stem: int) -> None:
    """Bảng tra thì phải tra được mọi can, không thủng ô nào."""
    assert 0 <= group3.place_luu_ha(stem) < 12, CAN[stem]
    assert 0 <= group3.place_thien_tru(stem) < 12, CAN[stem]


def test_luu_ha_khong_trung_cung_tren_moi_can() -> None:
    """Mười can cho mười vị trí khác nhau — bảng không có ô lặp.

    Đây chính là chỗ lý do chặn cũ hiểu sai: bảng *bất quy tắc* ở hai ô cuối, nhưng
    bất quy tắc không có nghĩa là chép sai.
    """
    assert len({group3.place_luu_ha(s) for s in range(10)}) == 10


@pytest.mark.parametrize("month", range(1, 13))
def test_thien_y_luon_dong_cung_thien_dieu(month: int) -> None:
    """Hệ quả trực tiếp của luật đã chọn — và là chỗ nó sẽ lộ ra nếu sai.

    Nếu bản đối chiếu đặt Thiên Y khác Thiên Diêu, luật này sai, và bài test vỡ ở
    đây chứ không vỡ âm thầm trên lá số của khách.
    """
    assert group3.place_thien_y(month) == group3.place_thien_dieu(month)


def test_giai_than_theo_cung_mo_tam_hop_chi_nam() -> None:
    """Biến thể đang chọn, sau khi lá số đối chiếu bác bỏ biến thể theo tháng.

    Bốn tam hợp cho bốn cung mộ, nên mười hai chi chỉ ra **bốn** vị trí.
    """
    positions = [group3.place_giai_than(b) for b in range(12)]
    assert len(set(positions)) == 4
    assert positions[CHI.index("Mão")] == CHI.index("Mùi")


def test_giai_than_luon_dong_cung_hoa_cai() -> None:
    """Hệ quả của luật đã chọn — và chỗ người thẩm định cần soi.

    Hai sao khác nhau mà không bao giờ rời nhau là điều đáng ngờ: hoặc đó là tính
    chất thật của cặp này, hoặc một trong hai luật đã chép nhầm sang cái kia. Lá số
    đối chiếu đặt cả hai ở Mùi nên nó **không** phân biệt được hai khả năng ấy.
    Viết ra đây để điều đó không trôi đi trong im lặng.
    """
    for branch in range(12):
        assert group3.place_giai_than(branch) == group2.place_hoa_cai(branch)


def test_bang_thien_tru_noi_ro_chin_hang_chua_co_bang_chung() -> None:
    """Bảng Thiên Trù mang xuất xứ từng hàng, không một nhãn chung cho cả bảng.

    Lá số đối chiếu đã bắt được **một** hàng sai. Điều đó chứng minh trí nhớ không
    đáng tin ở bảng này, nhưng không cho biết chín hàng kia sai chỗ nào — nên hai
    loại ô phải phân biệt được bằng máy, không phải bằng một dòng ghi chú.
    """
    assert len(group3.THIEN_TRU_BY_YEAR_STEM) == 10
    assert len(group3.THIEN_TRU_UNVERIFIED_STEMS) == 9
    assert group3.place_thien_tru(CAN.index("Kỷ")) == CHI.index("Thân")


def test_bang_do_sang_sai_bi_bac_bo_boi_la_so_doi_chieu() -> None:
    """Cái chốt: một bảng miếu vượng chép sai phải trượt trước khi lên lá số khách.

    Dựng một bảng đủ 12 ô cho Tử Vi nhưng đặt sai đúng ô mà lá số đối chiếu biết
    (Tử Vi tại Dần = Miếu). Bảng rỗng thì không bị bác bỏ — chưa điền thì chưa mâu
    thuẫn với gì — nhưng bảng đã điền mà lệch thì phải lộ ra.
    """
    from dataclasses import replace

    from cosmic_astrology.chart.types import StarStrength
    from cosmic_astrology.stars.reference import validate_strength_table
    from cosmic_astrology.stars.strength import NAM_PHAI_STAR_STRENGTH_V1

    assert validate_strength_table(NAM_PHAI_STAR_STRENGTH_V1) == ()

    wrong = replace(
        NAM_PHAI_STAR_STRENGTH_V1,
        entries={"TU_VI": {branch: StarStrength.HAM for branch in CHI}},
    )
    mismatches = validate_strength_table(wrong)
    assert len(mismatches) == 1
    assert mismatches[0].star_id == "TU_VI"
    assert mismatches[0].branch == "Dần"
    assert mismatches[0].expected is StarStrength.MIEU
