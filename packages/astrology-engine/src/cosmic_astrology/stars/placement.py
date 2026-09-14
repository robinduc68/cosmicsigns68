"""An phụ tinh — nhóm 1, theo Nam phái.

Mỗi hàm ở đây trả về **một chỉ số địa chi** (0 = Tý … 11 = Hợi) và không biết gì
về tên cung. Sao bám vào địa chi; tên cung là một phép gán riêng, và toạ độ trên
lưới lại là chuyện thứ ba. Lẫn ba khái niệm này chính là nguồn gốc lỗi lật gương
tên cung ở engine 0.1.0, nên ranh giới được giữ bằng kiểu trả về.

**Không quy tắc nào ở đây có nguồn đã chốt.** Cosmic Signs chưa chọn ấn bản chuẩn
(Q1/Q2/Q3), nên toàn bộ là cách đọc thông dụng của Nam phái, ghi ở mức
``PROVISIONAL``, và mỗi chỗ các trường phái ghi khác nhau đều được nêu trong
``docs/astrology-conventions.md`` §26. Việc tách hẳn ra một module thế này là để
đổi một luật sau này chỉ phải sửa một hàm.
"""

from __future__ import annotations

from cosmic_astrology.calendar.sexagenary import CAN, CHI

__all__ = [
    "place_da_la",
    "place_dao_hoa",
    "place_hong_loan",
    "place_huu_bat",
    "place_kinh_duong",
    "place_loc_ton",
    "place_ta_phu",
    "place_thien_hy",
    "place_thien_khoi",
    "place_thien_ma",
    "place_thien_viet",
    "place_van_khuc",
    "place_van_xuong",
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


def _check_branch(value: int, name: str) -> int:
    if not 0 <= value <= 11:
        raise ValueError(f"{name}: chỉ số địa chi phải trong 0–11, nhận {value}")
    return value


# --------------------------------------------------------------- Xương / Khúc


def place_van_xuong(hour_branch: int) -> int:
    """Văn Xương: khởi từ Tuất, đếm **nghịch** theo giờ sinh."""
    _check_branch(hour_branch, "giờ sinh")
    return (_TUAT - hour_branch) % 12


def place_van_khuc(hour_branch: int) -> int:
    """Văn Khúc: khởi từ Thìn, đếm **thuận** theo giờ sinh.

    Xương và Khúc **không** đối cung nhau: chúng đối xứng qua trục Thìn–Tuất, nên
    đồng cung tại Mùi (giờ Mão) và tại Sửu (giờ Dậu) — chính là cách "Xương Khúc
    đồng cung Sửu Mùi" mà sách hay nhắc. Đây là bất biến để kiểm bảng này.
    """
    _check_branch(hour_branch, "giờ sinh")
    return (_THIN + hour_branch) % 12


# ------------------------------------------------------------- Tả Phù / Hữu Bật


def _check_month(lunar_month: int) -> int:
    if not 1 <= lunar_month <= 12:
        raise ValueError(f"Tháng âm phải trong 1–12, nhận {lunar_month}")
    return lunar_month


def place_ta_phu(lunar_month: int) -> int:
    """Tả Phù: khởi từ Thìn tháng Giêng, đếm **thuận** theo tháng âm."""
    _check_month(lunar_month)
    return (_THIN + lunar_month - 1) % 12


def place_huu_bat(lunar_month: int) -> int:
    """Hữu Bật: khởi từ Tuất tháng Giêng, đếm **nghịch** theo tháng âm."""
    _check_month(lunar_month)
    return (_TUAT - (lunar_month - 1)) % 12


# ---------------------------------------------------------- Thiên Khôi / Việt

#: Bảng theo thiên can năm sinh, đọc từ câu quyết:
#: "Giáp Mậu Canh ngưu dương · Ất Kỷ thử hầu hương · Bính Đinh trư kê vị ·
#:  Nhâm Quý thỏ xà tàng · Lục Tân phùng mã hổ".
_KHOI_VIET_BY_STEM: dict[int, tuple[int, int]] = {
    CAN.index("Giáp"): (_SUU, _MUI),
    CAN.index("Mậu"): (_SUU, _MUI),
    CAN.index("Canh"): (_SUU, _MUI),
    CAN.index("Ất"): (_TY, _THAN),
    CAN.index("Kỷ"): (_TY, _THAN),
    CAN.index("Bính"): (_HOI, _DAU),
    CAN.index("Đinh"): (_HOI, _DAU),
    CAN.index("Nhâm"): (_MAO, _TY_RAN),
    CAN.index("Quý"): (_MAO, _TY_RAN),
    CAN.index("Tân"): (_NGO, _DAN),
}


def _check_stem(year_stem: int) -> int:
    if not 0 <= year_stem <= 9:
        raise ValueError(f"Thiên can phải trong 0–9, nhận {year_stem}")
    return year_stem


def place_thien_khoi(year_stem: int) -> int:
    """Thiên Khôi theo thiên can năm sinh."""
    return _KHOI_VIET_BY_STEM[_check_stem(year_stem)][0]


def place_thien_viet(year_stem: int) -> int:
    """Thiên Việt theo thiên can năm sinh."""
    return _KHOI_VIET_BY_STEM[_check_stem(year_stem)][1]


# ------------------------------------------------- Lộc Tồn / Kình Dương / Đà La

#: Lộc Tồn theo thiên can năm sinh — cung lâm quan của can đó.
_LOC_TON_BY_STEM: dict[int, int] = {
    CAN.index("Giáp"): _DAN,
    CAN.index("Ất"): _MAO,
    CAN.index("Bính"): _TY_RAN,
    CAN.index("Đinh"): _NGO,
    CAN.index("Mậu"): _TY_RAN,
    CAN.index("Kỷ"): _NGO,
    CAN.index("Canh"): _THAN,
    CAN.index("Tân"): _DAU,
    CAN.index("Nhâm"): _HOI,
    CAN.index("Quý"): _TY,
}


def place_loc_ton(year_stem: int) -> int:
    """Lộc Tồn theo thiên can năm sinh."""
    return _LOC_TON_BY_STEM[_check_stem(year_stem)]


def place_kinh_duong(loc_ton_branch: int) -> int:
    """Kình Dương: cung liền **sau** Lộc Tồn theo chiều thuận ("tiền Kình")."""
    return (_check_branch(loc_ton_branch, "Lộc Tồn") + 1) % 12


def place_da_la(loc_ton_branch: int) -> int:
    """Đà La: cung liền **trước** Lộc Tồn ("hậu Đà")."""
    return (_check_branch(loc_ton_branch, "Lộc Tồn") - 1) % 12


# ------------------------------------------------- Đào Hoa / Hồng Loan / Thiên Hỷ

#: Đào Hoa theo tam hợp chi năm. Luôn rơi vào tứ chính (Tý Ngọ Mão Dậu).
_DAO_HOA_BY_YEAR_BRANCH: dict[int, int] = {
    _THAN: _DAU, _TY: _DAU, _THIN: _DAU,
    _DAN: _MAO, _NGO: _MAO, _TUAT: _MAO,
    _TY_RAN: _NGO, _DAU: _NGO, _SUU: _NGO,
    _HOI: _TY, _MAO: _TY, _MUI: _TY,
}  # fmt: skip


def place_dao_hoa(year_branch: int) -> int:
    """Đào Hoa theo tam hợp của chi năm sinh."""
    return _DAO_HOA_BY_YEAR_BRANCH[_check_branch(year_branch, "chi năm")]


def place_hong_loan(year_branch: int) -> int:
    """Hồng Loan: khởi từ Mão năm Tý, đếm **nghịch** theo chi năm."""
    return (_MAO - _check_branch(year_branch, "chi năm")) % 12


def place_thien_hy(year_branch: int) -> int:
    """Thiên Hỷ: luôn đối cung Hồng Loan."""
    return (place_hong_loan(year_branch) + 6) % 12


# ------------------------------------------------------------------ Thiên Mã

#: Thiên Mã (dịch mã) theo tam hợp chi năm. Luôn rơi vào tứ sinh (Dần Thân Tỵ Hợi).
_THIEN_MA_BY_YEAR_BRANCH: dict[int, int] = {
    _THAN: _DAN, _TY: _DAN, _THIN: _DAN,
    _DAN: _THAN, _NGO: _THAN, _TUAT: _THAN,
    _TY_RAN: _HOI, _DAU: _HOI, _SUU: _HOI,
    _HOI: _TY_RAN, _MAO: _TY_RAN, _MUI: _TY_RAN,
}  # fmt: skip


def place_thien_ma(year_branch: int) -> int:
    """Thiên Mã theo tam hợp của chi năm sinh."""
    return _THIEN_MA_BY_YEAR_BRANCH[_check_branch(year_branch, "chi năm")]
