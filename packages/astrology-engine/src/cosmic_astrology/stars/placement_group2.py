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

from cosmic_astrology.calendar.sexagenary import CAN, CHI

__all__ = [
    "BAC_SI_CYCLE",
    "THAI_TUE_CYCLE",
    "place_an_quang",
    "place_bac_si_member",
    "place_bat_toa",
    "place_dia_giai",
    "place_duong_phu",
    "place_hoa_cai",
    "place_long_tri",
    "place_nguyet_duc",
    "place_phong_cao",
    "place_phuong_cac",
    "place_quoc_an",
    "place_tam_thai",
    "place_thai_phu",
    "place_thai_tue_member",
    "place_thien_duc",
    "place_thien_giai",
    "place_thien_phuc",
    "place_thien_quan",
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


# ------------------------------------------------------- Thiên Quan / Thiên Phúc

#: Thiên Quan Quý Nhân theo thiên can năm sinh.
_THIEN_QUAN_BY_STEM: dict[int, int] = {
    CAN.index("Giáp"): _MUI, CAN.index("Ất"): _THIN, CAN.index("Bính"): _TY_RAN,
    CAN.index("Đinh"): _DAN, CAN.index("Mậu"): _MAO, CAN.index("Kỷ"): _DAU,
    CAN.index("Canh"): _HOI, CAN.index("Tân"): _DAU, CAN.index("Nhâm"): _TUAT,
    CAN.index("Quý"): _NGO,
}  # fmt: skip

#: Thiên Phúc Quý Nhân theo thiên can năm sinh.
_THIEN_PHUC_BY_STEM: dict[int, int] = {
    CAN.index("Giáp"): _DAU, CAN.index("Ất"): _THAN, CAN.index("Bính"): _TY,
    CAN.index("Đinh"): _HOI, CAN.index("Mậu"): _MAO, CAN.index("Kỷ"): _DAN,
    CAN.index("Canh"): _NGO, CAN.index("Tân"): _TY_RAN, CAN.index("Nhâm"): _NGO,
    CAN.index("Quý"): _TY_RAN,
}  # fmt: skip


def _stem(year_stem: int) -> int:
    if not 0 <= year_stem <= 9:
        raise ValueError(f"Thiên can phải trong 0–9, nhận {year_stem}")
    return year_stem


def place_thien_quan(year_stem: int) -> int:
    """Thiên Quan Quý Nhân theo thiên can năm sinh."""
    return _THIEN_QUAN_BY_STEM[_stem(year_stem)]


def place_thien_phuc(year_stem: int) -> int:
    """Thiên Phúc Quý Nhân theo thiên can năm sinh."""
    return _THIEN_PHUC_BY_STEM[_stem(year_stem)]


# --------------------------------------------------------- Thiên Giải / Địa Giải


def _month(lunar_month: int) -> int:
    if not 1 <= lunar_month <= 12:
        raise ValueError(f"Tháng âm phải trong 1–12, nhận {lunar_month}")
    return lunar_month


def place_thien_giai(lunar_month: int) -> int:
    """Thiên Giải: khởi Thân tháng Giêng, đếm thuận theo tháng âm."""
    return (_THAN + _month(lunar_month) - 1) % 12


def place_dia_giai(lunar_month: int) -> int:
    """Địa Giải: khởi Mùi tháng Giêng, đếm thuận theo tháng âm.

    Thiên Giải luôn đứng ngay sau Địa Giải một cung — hệ quả của hai mốc khởi.
    """
    return (_MUI + _month(lunar_month) - 1) % 12


# ---------------------------------------------------------- Thai Phụ / Phong Cáo


def place_thai_phu(hour_branch: int) -> int:
    """Thai Phụ: khởi Ngọ giờ Tý, đếm thuận theo giờ sinh.

    Phát biểu tương đương thường gặp là "Văn Khúc tiến 2 cung" — hai cách cho **cùng
    một kết quả** ở cả 12 giờ, vì Văn Khúc chính là Thìn + giờ.
    """
    return (_NGO + _branch(hour_branch, "giờ sinh")) % 12


def place_phong_cao(hour_branch: int) -> int:
    """Phong Cáo: khởi Dần giờ Tý, đếm thuận. Tương đương "Văn Khúc lùi 2 cung"."""
    return (_DAN + _branch(hour_branch, "giờ sinh")) % 12


# ---------------------------------------------------------- Quốc Ấn / Đường Phù


def place_quoc_an(loc_ton_branch: int) -> int:
    """Quốc Ấn: cách **Lộc Tồn** 8 cung theo chiều thuận.

    Bảng theo can năm mà các sách ghi ra đúng bằng offset cố định này ở cả 10 can —
    hai cách phát biểu độc lập trùng khớp, nên bảng kiểm được mà không cần nguồn ngoài.
    """
    return (_branch(loc_ton_branch, "Lộc Tồn") + 8) % 12


def place_duong_phu(loc_ton_branch: int) -> int:
    """Đường Phù: cách **Lộc Tồn** 5 cung theo chiều thuận."""
    return (_branch(loc_ton_branch, "Lộc Tồn") + 5) % 12


# ------------------------------------------------------------------- Hỷ Thần

#: Vòng Bác Sĩ, khởi tại **Lộc Tồn**. Chiều theo âm dương nam nữ, cùng luật với đại
#: vận. Nhóm này **chỉ an Hỷ Thần**; Đại Hao, Tiểu Hao… thuộc nhóm sau.
BAC_SI_CYCLE: tuple[str, ...] = (
    "BAC_SI",
    "LUC_SI",
    "THANH_LONG",
    "TIEU_HAO",
    "TUONG_QUAN",
    "TAU_THU",
    "PHI_LIEM",
    "HY_THAN",
    "BENH_PHU",
    "DAI_HAO",
    "PHUC_BINH",
    "QUAN_PHU_BS",
)


def place_bac_si_member(loc_ton_branch: int, star_id: str, *, forward: bool) -> int:
    """Vị trí một sao trong vòng Bác Sĩ, tính từ Lộc Tồn.

    ``forward`` là chiều đã quyết ở tầng trên (dương nam / âm nữ đi thuận) — module
    này không tự suy chiều, để chỉ có một chỗ trong engine quyết định điều đó.
    """
    try:
        offset = BAC_SI_CYCLE.index(star_id)
    except ValueError as exc:
        raise ValueError(f"{star_id} không thuộc vòng Bác Sĩ") from exc
    step = 1 if forward else -1
    return (_branch(loc_ton_branch, "Lộc Tồn") + step * offset) % 12
