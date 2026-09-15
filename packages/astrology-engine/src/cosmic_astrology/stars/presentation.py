"""Cột trái / cột phải của một lá số in — **siêu dữ liệu trình bày, không phải luận đoán**.

Một lá số Tử Vi in theo lối truyền thống không xếp phụ tinh tràn hàng qua hai cột. Nó
tách **cát tinh / trợ tinh** về một bên và **sát tinh / bại tinh** về bên kia, để người
đọc nhìn một cái là thấy thế cân bằng của cung.

Vì sao module này nằm ở engine chứ không ở renderer: renderer tuyệt đối không được rẽ
nhánh theo mã sao, và ``no-star-name-styling.spec.ts`` quét mã nguồn renderer để giữ
điều đó. Nơi biết "sao nào là cát, sao nào là sát" là chỗ này.

Vì sao nó tách khỏi ``catalog.py``: catalog giữ **siêu dữ liệu chiêm tinh** — ngũ hành,
âm dương, độ sáng. Cột trái/phải là **toạ độ trình bày**. Trộn hai thứ vào một chỗ là
cách một quyết định bố cục lặng lẽ trở thành một khẳng định về lá số.

**Cát/hung ở đây KHÔNG liên quan gì tới màu.** Màu là ngũ hành và chỉ là ngũ hành: một
sát tinh hành Mộc vẫn vẽ màu xanh lá. Hai khái niệm đi hai đường, và chúng gặp nhau ở
đúng một chỗ — cùng một ngôi sao mang cả hai.
"""

from __future__ import annotations

from enum import StrEnum

__all__ = ["TraditionalColumn", "column_for"]


class TraditionalColumn(StrEnum):
    """Cột mà một ngôi sao thuộc về trên lá số in."""

    #: Cát tinh, trợ tinh, quý tinh, phúc thiện tinh.
    LEFT = "LEFT"
    #: Sát tinh, bại tinh, hung tinh, hình/kỵ/hao/không-kiếp.
    RIGHT = "RIGHT"
    #: Bản in không cho thấy sao này thuộc bên nào một cách rõ ràng. Renderer cân hai
    #: cột theo một luật xác định — xem ``docs/chart-renderer.md`` mục 9k. Đây là
    #: "chưa biết", **không phải** "trung tính về cát hung".
    AUTO = "AUTO"


#: Cột trái — cát tinh, trợ tinh, quý tinh, phúc thiện tinh.
_LEFT: frozenset[str] = frozenset(
    {
        # Trợ tinh và văn tinh
        "TA_PHU", "HUU_BAT", "VAN_XUONG", "VAN_KHUC", "THIEN_KHOI", "THIEN_VIET",
        "LOC_TON", "THIEN_MA",
        # Quý tinh
        "AN_QUANG", "THIEN_QUY", "TAM_THAI", "BAT_TOA", "THAI_PHU", "PHONG_CAO",
        "LONG_TRI", "PHUONG_CAC", "THIEN_QUAN", "THIEN_PHUC",
        # Ấn tín
        "QUOC_AN", "DUONG_PHU",
        # Phúc thiện
        "THIEN_DUC", "NGUYET_DUC", "LONG_DUC", "PHUC_DUC_STAR", "THIEN_TRU", "THIEN_Y",
        "THIEN_GIAI", "DIA_GIAI", "GIAI_THAN", "HY_THAN",
        # Thọ / tài
        "THIEN_TAI", "THIEN_THO",
        # Đào hoa hệ cát
        "HONG_LOAN", "THIEN_HY", "DAO_HOA",
        # Vòng Bác Sĩ — nửa cát
        "BAC_SI", "LUC_SI", "THANH_LONG", "TUONG_QUAN", "TAU_THU",
        # Vòng Thái Tuế — nửa cát
        "THIEU_DUONG", "THIEU_AM",
    }
)  # fmt: skip

#: Cột phải — sát tinh, bại tinh, hung tinh.
_RIGHT: frozenset[str] = frozenset(
    {
        # Lục sát
        "KINH_DUONG", "DA_LA", "HOA_TINH", "LINH_TINH", "DIA_KHONG", "DIA_KIEP",
        # Không vong / hình kỵ
        "THIEN_KHONG", "THIEN_HINH", "THIEN_DIEU", "KIEP_SAT", "PHA_TOAI", "LUU_HA",
        "THIEN_LA", "DIA_VONG",
        # Hao
        "DAI_HAO", "TIEU_HAO",
        # Tang khốc
        "TANG_MON", "BACH_HO", "THIEN_KHOC", "THIEN_HU", "TU_PHU", "BENH_PHU",
        # Cô quả
        "CO_THAN", "QUA_TU",
        # Quan tụng
        "QUAN_PHU_TT", "QUAN_PHU_BS", "DIEU_KHACH", "TRUC_PHU",
        # Thương sứ
        "THIEN_THUONG", "THIEN_SU",
        # Vòng Thái Tuế — nửa hung
        "THAI_TUE", "TUE_PHA",
        # Vòng Bác Sĩ — nửa hung
        "PHI_LIEM", "PHUC_BINH",
    }
)  # fmt: skip

#: Tiền tố của lưu tinh. Một lưu tinh **dùng lại cột của sao gốc**: "L.Kình Dương" là
#: Kình Dương của năm xem, và nó không đổi phe vì đổi lớp.
_ANNUAL_PREFIX = "LUU_"


def column_for(star_id: str, base_star_id: str | None = None) -> TraditionalColumn:
    """Cột của một ngôi sao. ``base_star_id`` dùng cho lưu tinh.

    Chính tinh **không** thuộc phép chia này — chúng nằm ở khối giữa cung — nên chúng
    rơi vào ``AUTO`` và renderer không bao giờ hỏi tới.
    """
    for candidate in (star_id, base_star_id):
        if candidate is None:
            continue
        if candidate in _LEFT:
            return TraditionalColumn.LEFT
        if candidate in _RIGHT:
            return TraditionalColumn.RIGHT
    # Lưu tinh chưa có sao gốc trong catalog: thử bỏ tiền tố.
    if star_id.startswith(_ANNUAL_PREFIX):
        stripped = star_id[len(_ANNUAL_PREFIX) :]
        if stripped in _LEFT:
            return TraditionalColumn.LEFT
        if stripped in _RIGHT:
            return TraditionalColumn.RIGHT
    return TraditionalColumn.AUTO
