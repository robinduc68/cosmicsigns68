"""An sát tinh / bại tinh — nhóm 1, theo Nam phái.

Cùng kỷ luật: mỗi hàm trả về **một chỉ số địa chi**, không biết gì về tên cung.

**Sáu sao không có mặt ở đây vì chúng đã thuộc chu kỳ có sẵn** — viết lại là tạo ra
nguồn sự thật thứ hai:

| Sao | Nằm ở | Offset |
| --- | --- | --- |
| Tang Môn, Quan Phù, Bạch Hổ, Điếu Khách | `placement_group2.THAI_TUE_CYCLE` | +2, +4, +8, +10 |
| Tiểu Hao, Đại Hao | `placement_group2.BAC_SI_CYCLE` | +3, +9 |

**Phụ thuộc đầu vào** của mười sao còn lại:

| Sao | Phụ thuộc |
| --- | --- |
| Địa Không, Địa Kiếp | giờ sinh |
| Hỏa Tinh, Linh Tinh | chi năm (tam hợp) + giờ sinh + chiều theo âm dương nam nữ |
| Kiếp Sát | chi năm (tam hợp) |
| Cô Thần, Quả Tú | chi năm (theo mùa) |
| Thiên Không | chi năm |
| Thiên Khốc, Thiên Hư | chi năm |

**Địa Không và Thiên Không là hai sao khác nhau**, khác luật, khác mã. Chúng chỉ
tình cờ chung chữ "Không".
"""

from __future__ import annotations

from cosmic_astrology.calendar.sexagenary import CHI

__all__ = [
    "place_co_than",
    "place_dia_khong",
    "place_dia_kiep",
    "place_hoa_tinh",
    "place_kiep_sat",
    "place_linh_tinh",
    "place_qua_tu",
    "place_thien_hu",
    "place_thien_khoc",
    "place_thien_khong",
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


# ------------------------------------------------------- Địa Không / Địa Kiếp


def place_dia_kiep(hour_branch: int) -> int:
    """Địa Kiếp: khởi Hợi giờ Tý, đếm **thuận** theo giờ sinh."""
    return (_HOI + _branch(hour_branch, "giờ sinh")) % 12


def place_dia_khong(hour_branch: int) -> int:
    """Địa Không: khởi Hợi giờ Tý, đếm **nghịch** theo giờ sinh.

    Hai sao đối xứng qua trục Tỵ–Hợi, nên **đồng cung tại Hợi (giờ Tý) và Tỵ (giờ
    Ngọ)** — bất biến để kiểm.

    Đây **không phải** Thiên Không; xem ``place_thien_khong``.
    """
    return (_HOI - _branch(hour_branch, "giờ sinh")) % 12


# ------------------------------------------------------- Hỏa Tinh / Linh Tinh

#: Địa chi khởi của Hỏa Tinh và Linh Tinh theo tam hợp chi năm, đọc từ câu quyết
#: "Dần Ngọ Tuất nhân Sửu Mão phương · Thân Tý Thìn nhân Dần Tuất dương ·
#:  Tỵ Dậu Sửu nhân Mão Tuất vị · Hợi Mão Mùi nhân Dậu Tuất phòng".
_HOA_LINH_START: dict[int, tuple[int, int]] = {
    _DAN: (_SUU, _MAO), _NGO: (_SUU, _MAO), _TUAT: (_SUU, _MAO),
    _THAN: (_DAN, _TUAT), _TY: (_DAN, _TUAT), _THIN: (_DAN, _TUAT),
    _TY_RAN: (_MAO, _TUAT), _DAU: (_MAO, _TUAT), _SUU: (_MAO, _TUAT),
    _HOI: (_DAU, _TUAT), _MAO: (_DAU, _TUAT), _MUI: (_DAU, _TUAT),
}  # fmt: skip


def place_hoa_tinh(year_branch: int, hour_branch: int, *, forward: bool) -> int:
    """Hỏa Tinh: từ địa chi khởi của tam hợp chi năm, đếm theo giờ sinh.

    ``forward`` do tầng trên quyết (dương nam / âm nữ đi thuận) — module này không
    tự suy chiều, để engine chỉ có một chỗ quyết định điều đó.
    """
    start = _HOA_LINH_START[_branch(year_branch, "chi năm")][0]
    step = 1 if forward else -1
    return (start + step * _branch(hour_branch, "giờ sinh")) % 12


def place_linh_tinh(year_branch: int, hour_branch: int, *, forward: bool) -> int:
    """Linh Tinh: cùng cách với Hỏa Tinh, khác địa chi khởi."""
    start = _HOA_LINH_START[_branch(year_branch, "chi năm")][1]
    step = 1 if forward else -1
    return (start + step * _branch(hour_branch, "giờ sinh")) % 12


# ------------------------------------------------------------------ Kiếp Sát

#: Kiếp Sát theo tam hợp chi năm — luôn rơi vào **tứ sinh** (Dần Thân Tỵ Hợi).
_KIEP_SAT_BY_YEAR_BRANCH: dict[int, int] = {
    _THAN: _TY_RAN, _TY: _TY_RAN, _THIN: _TY_RAN,
    _DAN: _HOI, _NGO: _HOI, _TUAT: _HOI,
    _TY_RAN: _DAN, _DAU: _DAN, _SUU: _DAN,
    _HOI: _THAN, _MAO: _THAN, _MUI: _THAN,
}  # fmt: skip


def place_kiep_sat(year_branch: int) -> int:
    """Kiếp Sát: cung tuyệt của tam hợp chi năm."""
    return _KIEP_SAT_BY_YEAR_BRANCH[_branch(year_branch, "chi năm")]


# -------------------------------------------------------- Cô Thần / Quả Tú

#: Cô Thần và Quả Tú theo **mùa** của chi năm (ba chi liền nhau một nhóm).
#: Cô Thần luôn ở tứ sinh, Quả Tú luôn ở tứ mộ, và hai sao luôn cách nhau 4 cung.
_CO_QUA_BY_YEAR_BRANCH: dict[int, tuple[int, int]] = {
    _HOI: (_DAN, _TUAT), _TY: (_DAN, _TUAT), _SUU: (_DAN, _TUAT),
    _DAN: (_TY_RAN, _SUU), _MAO: (_TY_RAN, _SUU), _THIN: (_TY_RAN, _SUU),
    _TY_RAN: (_THAN, _THIN), _NGO: (_THAN, _THIN), _MUI: (_THAN, _THIN),
    _THAN: (_HOI, _MUI), _DAU: (_HOI, _MUI), _TUAT: (_HOI, _MUI),
}  # fmt: skip


def place_co_than(year_branch: int) -> int:
    """Cô Thần theo mùa của chi năm sinh."""
    return _CO_QUA_BY_YEAR_BRANCH[_branch(year_branch, "chi năm")][0]


def place_qua_tu(year_branch: int) -> int:
    """Quả Tú theo mùa của chi năm sinh."""
    return _CO_QUA_BY_YEAR_BRANCH[_branch(year_branch, "chi năm")][1]


# ---------------------------------------------------------------- Thiên Không


def place_thien_khong(year_branch: int) -> int:
    """Thiên Không: cung liền sau Thái Tuế theo chiều thuận.

    Hệ quả: **luôn đồng cung với Thiếu Dương**, vì Thiếu Dương cũng ở offset +1 của
    vòng Thái Tuế. Đó là kết quả đúng, không phải trùng lặp cần khử.

    Sao này **khác Địa Không** hoàn toàn — khác luật, khác mã, chỉ chung chữ.
    """
    return (_branch(year_branch, "chi năm") + 1) % 12


# ------------------------------------------------------ Thiên Khốc / Thiên Hư


def place_thien_khoc(year_branch: int) -> int:
    """Thiên Khốc: khởi Ngọ năm Tý, đếm **nghịch** theo chi năm."""
    return (_NGO - _branch(year_branch, "chi năm")) % 12


def place_thien_hu(year_branch: int) -> int:
    """Thiên Hư: khởi Ngọ năm Tý, đếm **thuận** theo chi năm.

    Cặp đối xứng qua trục Tý–Ngọ: hai sao **đồng cung tại Ngọ (năm Tý)** và tại Tý
    (năm Ngọ). Quan hệ này viết thẳng ra đây thay vì lặp lại số học ở nơi khác.
    """
    return (_NGO + _branch(year_branch, "chi năm")) % 12
