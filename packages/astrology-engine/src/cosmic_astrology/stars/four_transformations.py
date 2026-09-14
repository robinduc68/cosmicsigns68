"""Bảng Tứ Hóa — Nam phái.

Tứ Hóa **không phải bốn ngôi sao**. Nó là bốn *trạng thái* mà một ngôi sao đã an
sẵn có thể mang, quyết định bởi **thiên can năm sinh**. Vì thế ở đây không có hàm
an sao nào: bảng chỉ nói "can này thì sao nào hóa gì", còn việc gắn trạng thái vào
đúng ngôi sao là của ``chart.builder``.

**Đây là mục phụ thuộc trường phái nặng nhất của toàn bộ hệ thống.** Hàng Canh có
ba biến thể được ghi nhận, và hai trong số đó **đảo ngược Khoa với Kỵ** — tức đảo
một cát tinh thành hung tinh trên mọi lá số sinh năm Canh. Cả ba biến thể đều nằm
trong file này, để chọn lại chỉ là đổi một hằng số chứ không phải sửa bảng.

Mọi hàng ở mức ``PROVISIONAL``. Xem ``docs/astrology-conventions.md`` §15.
"""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

from cosmic_astrology.calendar.sexagenary import CAN
from cosmic_astrology.chart.model import Transformation

__all__ = [
    "CANH_VARIANTS",
    "NAM_PHAI_FOUR_TRANSFORMATIONS_V1",
    "TABLE_VERSION",
    "transformations_for_stem",
]

#: Bumped when a row changes. Lá số đã lưu mang số này nên đổi bảng là phát hiện được.
TABLE_VERSION = "NAM_PHAI_V1"

L = Transformation.HOA_LOC
Q = Transformation.HOA_QUYEN
K = Transformation.HOA_KHOA
KY = Transformation.HOA_KY

#: Ba cách đọc hàng Canh đã được ghi nhận. Hai cách đầu **đổi chỗ Khoa và Kỵ**,
#: nên chọn nhầm không làm lá số sai một chi tiết — nó lật ngược ý nghĩa.
CANH_VARIANTS: Mapping[str, Mapping[Transformation, str]] = MappingProxyType(
    {
        # Phương án 1 — đa số bản Việt. Đang được chọn.
        "THAI_AM_KHOA_THIEN_DONG_KY": MappingProxyType(
            {L: "THAI_DUONG", Q: "VU_KHUC", K: "THAI_AM", KY: "THIEN_DONG"}
        ),
        # Phương án 2 — đảo Khoa/Kỵ so với phương án 1.
        "THIEN_DONG_KHOA_THAI_AM_KY": MappingProxyType(
            {L: "THAI_DUONG", Q: "VU_KHUC", K: "THIEN_DONG", KY: "THAI_AM"}
        ),
        # Phương án 3 — Khoa về Thiên Phủ.
        "THIEN_PHU_KHOA_THIEN_DONG_KY": MappingProxyType(
            {L: "THAI_DUONG", Q: "VU_KHUC", K: "THIEN_PHU", KY: "THIEN_DONG"}
        ),
    }
)

#: Phương án hàng Canh đang dùng. Đổi hằng số này là đổi cả bảng — đó là chủ ý:
#: quyết định nằm ở một chỗ đọc được, không rải trong logic.
SELECTED_CANH_VARIANT = "THAI_AM_KHOA_THIEN_DONG_KY"


def _row(loc: str, quyen: str, khoa: str, ky: str) -> Mapping[Transformation, str]:
    return MappingProxyType({L: loc, Q: quyen, K: khoa, KY: ky})


#: Bảng Tứ Hóa theo thiên can năm sinh. Giá trị là **mã sao** trong
#: ``stars.catalog`` — không phải tên hiển thị, để đổi tên không làm hỏng bảng.
NAM_PHAI_FOUR_TRANSFORMATIONS_V1: Mapping[str, Mapping[Transformation, str]] = MappingProxyType(
    {
        "Giáp": _row("LIEM_TRINH", "PHA_QUAN", "VU_KHUC", "THAI_DUONG"),
        "Ất": _row("THIEN_CO", "THIEN_LUONG", "TU_VI", "THAI_AM"),
        "Bính": _row("THIEN_DONG", "THIEN_CO", "VAN_XUONG", "LIEM_TRINH"),
        "Đinh": _row("THAI_AM", "THIEN_DONG", "THIEN_CO", "CU_MON"),
        # Hàng Mậu: Hóa Khoa có biến thể (Hữu Bật / Thái Dương). Chọn Hữu Bật.
        "Mậu": _row("THAM_LANG", "THAI_AM", "HUU_BAT", "THIEN_CO"),
        "Kỷ": _row("VU_KHUC", "THAM_LANG", "THIEN_LUONG", "VAN_KHUC"),
        "Canh": CANH_VARIANTS[SELECTED_CANH_VARIANT],
        "Tân": _row("CU_MON", "THAI_DUONG", "VAN_KHUC", "VAN_XUONG"),
        # Hàng Nhâm: Hóa Khoa có biến thể (Tả Phù / Thiên Phủ). Chọn Tả Phù.
        "Nhâm": _row("THIEN_LUONG", "TU_VI", "TA_PHU", "VU_KHUC"),
        "Quý": _row("PHA_QUAN", "CU_MON", "THAI_AM", "THAM_LANG"),
    }
)


def transformations_for_stem(year_stem: int) -> Mapping[Transformation, str]:
    """Bốn hóa của một thiên can năm sinh, dưới dạng ``{hóa: mã sao}``."""
    if not 0 <= year_stem <= 9:
        raise ValueError(f"Thiên can phải trong 0–9, nhận {year_stem}")
    return NAM_PHAI_FOUR_TRANSFORMATIONS_V1[CAN[year_stem]]
