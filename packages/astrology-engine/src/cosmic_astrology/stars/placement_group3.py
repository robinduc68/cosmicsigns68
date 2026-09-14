"""An phụ tinh — nhóm 3, theo Nam phái.

Chỉ chứa **luật mới**. Những sao chỉ là một offset của chu kỳ đã có (vòng Bác Sĩ,
vòng Thái Tuế) **không** xuất hiện ở đây — chúng được đọc thẳng từ chu kỳ đó, vì
một chu kỳ có hai cách tính là một lỗi chờ sẵn.

**Phụ thuộc đầu vào:**

| Sao | Phụ thuộc |
| --- | --- |
| Phá Toái | chi năm (theo nhóm tứ chính / tứ sinh / tứ mộ) |
| Thiên Hình, Thiên Diêu | tháng âm |
| Thiên La, Địa Võng | **cố định** — Thìn và Tuất, không phụ thuộc gì |
| Thiên Thương, Thiên Sứ | **vị trí cung** Nô Bộc và Tật Ách |
| Đẩu Quân | chi năm + tháng âm + giờ sinh |

Thiên Thương và Thiên Sứ gắn vào *cung*, nhưng hàm vẫn trả về **địa chi** — cung
nào nằm ở địa chi nào là việc engine đã biết, và frontend tuyệt đối không được tự
suy ra điều đó.
"""

from __future__ import annotations

from cosmic_astrology.calendar.sexagenary import CHI

__all__ = [
    "DIA_VONG_BRANCH",
    "THIEN_LA_BRANCH",
    "place_dau_quan",
    "place_pha_toai",
    "place_thien_dieu",
    "place_thien_hinh",
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

#: Thiên La và Địa Võng **cố định** tại Thìn và Tuất. Không có phép tính nào —
#: hằng số chứ không phải hàm, để không ai tưởng chúng phụ thuộc ngày sinh.
THIEN_LA_BRANCH = _THIN
DIA_VONG_BRANCH = _TUAT


def _branch(value: int, name: str) -> int:
    if not 0 <= value <= 11:
        raise ValueError(f"{name}: chỉ số địa chi phải trong 0–11, nhận {value}")
    return value


def _month(lunar_month: int) -> int:
    if not 1 <= lunar_month <= 12:
        raise ValueError(f"Tháng âm phải trong 1–12, nhận {lunar_month}")
    return lunar_month


# ------------------------------------------------------------------ Phá Toái

#: Phá Toái theo nhóm chi năm. Ba nhóm, ba kết quả — và cả ba đều nằm trong tam
#: hợp Tỵ–Dậu–Sửu, một đặc điểm dễ kiểm.
_PHA_TOAI_BY_YEAR_BRANCH: dict[int, int] = {
    _TY: _TY_RAN, _NGO: _TY_RAN, _MAO: _TY_RAN, _DAU: _TY_RAN,
    _DAN: _SUU, _THAN: _SUU, _TY_RAN: _SUU, _HOI: _SUU,
    _THIN: _DAU, _TUAT: _DAU, _SUU: _DAU, _MUI: _DAU,
}  # fmt: skip


def place_pha_toai(year_branch: int) -> int:
    """Phá Toái: tứ chính → Tỵ, tứ sinh → Sửu, tứ mộ → Dậu."""
    return _PHA_TOAI_BY_YEAR_BRANCH[_branch(year_branch, "chi năm")]


# -------------------------------------------------------- Thiên Hình / Thiên Diêu


def place_thien_hinh(lunar_month: int) -> int:
    """Thiên Hình: khởi Dậu tháng Giêng, đếm thuận theo tháng âm."""
    return (_DAU + _month(lunar_month) - 1) % 12


def place_thien_dieu(lunar_month: int) -> int:
    """Thiên Diêu: khởi Sửu tháng Giêng, đếm thuận theo tháng âm.

    Hình và Diêu cùng bước theo tháng nên **luôn cách nhau 8 cung** — bất biến để
    kiểm bảng.
    """
    return (_SUU + _month(lunar_month) - 1) % 12


# ------------------------------------------------------------------ Đẩu Quân


def place_dau_quan(year_branch: int, lunar_month: int, hour_branch: int) -> int:
    """Đẩu Quân: từ Thái Tuế đếm **nghịch** tới tháng sinh, rồi đếm **thuận** tới giờ.

    Hai bước ngược chiều nhau, nên đây là một trong số ít sao dùng cả ba đầu vào
    chi năm, tháng âm và giờ sinh.
    """
    after_month = (_branch(year_branch, "chi năm") - (_month(lunar_month) - 1)) % 12
    return (after_month + _branch(hour_branch, "giờ sinh")) % 12
