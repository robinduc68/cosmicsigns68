"""An phụ tinh — nhóm 2, theo Nam phái.

Cùng kỷ luật với nhóm 1: mỗi hàm trả về **một chỉ số địa chi** và không biết gì về
tên cung. Tách riêng khỏi ``placement.py`` để nhóm 1 không bị đụng tới.

**Phụ thuộc đầu vào** — nêu ngay trên chữ ký hàm, không giấu trong tiện ích chung:

| Sao | Phụ thuộc |
| --- | --- |
| Long Trì, Phượng Các | chi năm |
| Thiên Đức, Nguyệt Đức | chi năm |
| Hoa Cái | chi năm (tam hợp) |
| Thiếu Dương, Thiếu Âm, Long Đức, Phúc Đức | chi năm (vòng Thái Tuế) |
| Tam Thai | **Tả Phù** + ngày âm |
| Bát Tọa | **Hữu Bật** + ngày âm |
| Ân Quang | **Văn Xương** + ngày âm |
| Thiên Quý | **Văn Khúc** + ngày âm |
| Thiên Tài | **cung Mệnh** + chi năm |
| Thiên Thọ | **cung Thân** + chi năm |

Sáu sao cuối phụ thuộc vị trí sao/cung đã an, nên nhóm 2 **phải chạy sau** nhóm 1.

Không luật nào có nguồn đã chốt. Toàn bộ là cách đọc thông dụng của Nam phái, ghi ở
mức ``PROVISIONAL`` — xem ``docs/astrology-conventions.md`` §27.
"""

from __future__ import annotations

from cosmic_astrology.calendar.sexagenary import CHI

__all__ = [
    "THAI_TUE_CYCLE",
    "place_an_quang",
    "place_bat_toa",
    "place_hoa_cai",
    "place_long_tri",
    "place_nguyet_duc",
    "place_phuong_cac",
    "place_tam_thai",
    "place_thai_tue_member",
    "place_thien_duc",
    "place_thien_quy",
    "place_thien_tai",
    "place_thien_tho",
]

_TY = CHI.index("Tý")
_SUU = CHI.index("Sửu")
_DAN = CHI.index("Dần")
_MAO = CHI.index("Mão")
_THIN = CHI.index("Thìn")
_TY_RAN = CHI.index("Tỵ")
_NGO = CHI.index("Ngọ")
_MUI = CHI.index("Mùi")
_THAN = CHI.index("Thân")
_DAU = CHI.index("Dậu")
_TUAT = CHI.index("Tuất")
_HOI = CHI.index("Hợi")


def _branch(value: int, name: str) -> int:
    if not 0 <= value <= 11:
        raise ValueError(f"{name}: chỉ số địa chi phải trong 0–11, nhận {value}")
    return value


def _lunar_day(day: int) -> int:
    if not 1 <= day <= 30:
        raise ValueError(f"Ngày âm phải trong 1–30, nhận {day}")
    return day


# ------------------------------------------------------- Long Trì / Phượng Các


def place_long_tri(year_branch: int) -> int:
    """Long Trì: khởi Thìn năm Tý, đếm **thuận** theo chi năm."""
    return (_THIN + _branch(year_branch, "chi năm")) % 12


def place_phuong_cac(year_branch: int) -> int:
    """Phượng Các: khởi Tuất năm Tý, đếm **nghịch** theo chi năm.

    Long Trì và Phượng Các đối xứng qua trục Sửu–Mùi, nên **đồng cung tại Mùi
    (năm Mão) và Sửu (năm Dậu)** — bất biến để kiểm bảng này.
    """
    return (_TUAT - _branch(year_branch, "chi năm")) % 12


# ---------------------------------------------------------- Tam Thai / Bát Tọa


def place_tam_thai(ta_phu_branch: int, lunar_day: int) -> int:
    """Tam Thai: từ **Tả Phù**, đếm thuận tới ngày sinh (mùng 1 tại Tả Phù)."""
    return (_branch(ta_phu_branch, "Tả Phù") + _lunar_day(lunar_day) - 1) % 12


def place_bat_toa(huu_bat_branch: int, lunar_day: int) -> int:
    """Bát Tọa: từ **Hữu Bật**, đếm nghịch tới ngày sinh."""
    return (_branch(huu_bat_branch, "Hữu Bật") - (_lunar_day(lunar_day) - 1)) % 12


# --------------------------------------------------------- Ân Quang / Thiên Quý


def place_an_quang(van_xuong_branch: int, lunar_day: int) -> int:
    """Ân Quang: từ **Văn Xương** đếm thuận tới ngày sinh, rồi **lùi một cung**."""
    return (_branch(van_xuong_branch, "Văn Xương") + _lunar_day(lunar_day) - 2) % 12


def place_thien_quy(van_khuc_branch: int, lunar_day: int) -> int:
    """Thiên Quý: từ **Văn Khúc** đếm thuận tới ngày sinh, rồi **lùi một cung**."""
    return (_branch(van_khuc_branch, "Văn Khúc") + _lunar_day(lunar_day) - 2) % 12


# ------------------------------------------------------- Thiên Đức / Nguyệt Đức


def place_thien_duc(year_branch: int) -> int:
    """Thiên Đức: khởi Dậu năm Tý, đếm thuận theo chi năm."""
    return (_DAU + _branch(year_branch, "chi năm")) % 12


def place_nguyet_duc(year_branch: int) -> int:
    """Nguyệt Đức: khởi Tỵ năm Tý, đếm thuận theo chi năm.

    Thiên Đức và Nguyệt Đức luôn cách nhau 4 cung — hệ quả của hai mốc khởi.
    """
    return (_TY_RAN + _branch(year_branch, "chi năm")) % 12


# ----------------------------------------------------------------- Vòng Thái Tuế

#: Vòng Thái Tuế, khởi tại chi năm sinh và đi thuận. Nhóm này **chỉ an bốn sao**;
#: Tang Môn, Bạch Hổ, Quan Phù, Điếu Khách… thuộc nhóm sau, nên cố ý không có mặt.
THAI_TUE_CYCLE: tuple[str, ...] = (
    "THAI_TUE",
    "THIEU_DUONG",
    "TANG_MON",
    "THIEU_AM",
    "QUAN_PHU_TT",
    "TU_PHU",
    "TUE_PHA",
    "LONG_DUC",
    "BACH_HO",
    "PHUC_DUC_STAR",
    "DIEU_KHACH",
    "TRUC_PHU",
)


def place_thai_tue_member(year_branch: int, star_id: str) -> int:
    """Vị trí một sao trong vòng Thái Tuế, tính từ chi năm sinh đi thuận."""
    try:
        offset = THAI_TUE_CYCLE.index(star_id)
    except ValueError as exc:
        raise ValueError(f"{star_id} không thuộc vòng Thái Tuế") from exc
    return (_branch(year_branch, "chi năm") + offset) % 12


# --------------------------------------------------------------------- Hoa Cái

#: Hoa Cái theo tam hợp chi năm — luôn rơi vào **tứ mộ** (Thìn Tuất Sửu Mùi).
_HOA_CAI_BY_YEAR_BRANCH: dict[int, int] = {
    _THAN: _THIN, _TY: _THIN, _THIN: _THIN,
    _DAN: _TUAT, _NGO: _TUAT, _TUAT: _TUAT,
    _TY_RAN: _SUU, _DAU: _SUU, _SUU: _SUU,
    _HOI: _MUI, _MAO: _MUI, _MUI: _MUI,
}  # fmt: skip


def place_hoa_cai(year_branch: int) -> int:
    """Hoa Cái: cung mộ của tam hợp chi năm."""
    return _HOA_CAI_BY_YEAR_BRANCH[_branch(year_branch, "chi năm")]


# ------------------------------------------------------- Thiên Tài / Thiên Thọ


def place_thien_tai(menh_branch: int, year_branch: int) -> int:
    """Thiên Tài: từ **cung Mệnh**, đếm thuận theo chi năm."""
    return (_branch(menh_branch, "cung Mệnh") + _branch(year_branch, "chi năm")) % 12


def place_thien_tho(than_branch: int, year_branch: int) -> int:
    """Thiên Thọ: từ **cung Thân**, đếm thuận theo chi năm."""
    return (_branch(than_branch, "cung Thân") + _branch(year_branch, "chi năm")) % 12
