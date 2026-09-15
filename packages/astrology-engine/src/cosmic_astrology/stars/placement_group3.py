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
| Lưu Hà, Thiên Trù | **can năm** — bảng tra 10 ô, không có công thức |

Thiên Thương và Thiên Sứ gắn vào *cung*, nhưng hàm vẫn trả về **địa chi** — cung
nào nằm ở địa chi nào là việc engine đã biết, và frontend tuyệt đối không được tự
suy ra điều đó.
"""

from __future__ import annotations

from cosmic_astrology.calendar.sexagenary import CHI
from cosmic_astrology.stars import placement_group2 as group2

__all__ = [
    "DIA_VONG_BRANCH",
    "LUU_HA_BY_YEAR_STEM",
    "THIEN_LA_BRANCH",
    "THIEN_TRU_BY_YEAR_STEM",
    "THIEN_TRU_UNVERIFIED_STEMS",
    "place_dau_quan",
    "place_giai_than",
    "place_giai_than_by_month_pair",
    "place_luu_ha",
    "place_pha_toai",
    "place_thien_dieu",
    "place_thien_hinh",
    "place_thien_tru",
    "place_thien_y",
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


# --------------------------------------------------------------- Lưu Hà / Thiên Trù


def _stem(value: int, name: str) -> int:
    if not 0 <= value <= 9:
        raise ValueError(f"{name}: chỉ số thiên can phải trong 0–9, nhận {value}")
    return value


#: Lưu Hà theo can năm, khoá là **chỉ số can** (Giáp = 0).
#:
#: Dự án từng xếp sao này vào diện *chưa cài được*, với lý do "bảng có chỗ bất quy
#: tắc, không đối chiếu được". Tám ô đầu đi xuống rất đều — Dậu, Tuất, Mùi, Thân,
#: Tỵ, Ngọ, Thìn, Mão — rồi hai ô cuối nhảy sang Hợi và Dần. Người viết thấy chỗ
#: gãy ấy và kết luận mình nhớ sai bảng.
#:
#: Chỗ gãy **có thật trong bảng**. Nó là đặc điểm của bảng, không phải dấu hiệu chép
#: sai — và một bảng tra 10 ô thì không có "quy luật" nào bắt buộc phải đều. Lý do
#: chặn cũ vì vậy không đứng vững, nên sao này nay đã an, ở mức PROVISIONAL.
LUU_HA_BY_YEAR_STEM: dict[int, int] = {
    0: CHI.index("Dậu"),  # Giáp
    1: CHI.index("Tuất"),  # Ất
    2: CHI.index("Mùi"),  # Bính
    3: CHI.index("Thân"),  # Đinh
    4: CHI.index("Tỵ"),  # Mậu
    5: CHI.index("Ngọ"),  # Kỷ
    6: CHI.index("Thìn"),  # Canh
    7: CHI.index("Mão"),  # Tân
    8: CHI.index("Hợi"),  # Nhâm
    9: CHI.index("Dần"),  # Quý
}

#: Thiên Trù theo can năm, khoá là **chỉ số can** (Giáp = 0). Mỗi ô kèm **xuất xứ**:
#:
#:   ``OBSERVED``  — đọc trực tiếp từ lá số đối chiếu. Một ô, một lá số.
#:   ``RECALLED``  — người viết code nêu lại từ trí nhớ. **Chưa đối chiếu được.**
#:
#: Vì sao phải ghi xuất xứ từng ô thay vì gắn một nhãn PROVISIONAL cho cả bảng: lá số
#: đối chiếu cho thấy hàng Kỷ của bảng nêu-lại là **sai** (nó ghi Mão, lá số ghi
#: Thân). Một hàng sai đã chứng minh trí nhớ không đáng tin ở bảng này, nhưng không
#: cho biết chín hàng kia sai chỗ nào. Gộp tất cả vào một nhãn sẽ che mất đúng sự
#: khác biệt ấy — giữa một ô *có bằng chứng* và chín ô *chỉ có trí nhớ đã bị bắt lỗi*.
#:
#: Bảng này cũng **không có cấu trúc nội tại nào để tự kiểm** (không đối xứng, có ô
#: lặp), nên không test nào bắt được lỗi chép ở chín hàng còn lại. Đây là chỗ cần một
#: ấn bản sớm nhất trong cả engine.
THIEN_TRU_BY_YEAR_STEM: dict[int, tuple[int, str]] = {
    0: (CHI.index("Tỵ"), "RECALLED"),  # Giáp
    1: (CHI.index("Ngọ"), "RECALLED"),  # Ất
    2: (CHI.index("Tý"), "RECALLED"),  # Bính
    3: (CHI.index("Sửu"), "RECALLED"),  # Đinh
    4: (CHI.index("Dần"), "RECALLED"),  # Mậu
    5: (CHI.index("Thân"), "OBSERVED"),  # Kỷ — lá số đối chiếu 13/10/1999
    6: (CHI.index("Dậu"), "RECALLED"),  # Canh
    7: (CHI.index("Tuất"), "RECALLED"),  # Tân
    8: (CHI.index("Ngọ"), "RECALLED"),  # Nhâm
    9: (CHI.index("Tỵ"), "RECALLED"),  # Quý
}

#: Những can mà bảng Thiên Trù **chưa có bằng chứng nào** chống lưng.
THIEN_TRU_UNVERIFIED_STEMS: tuple[int, ...] = tuple(
    stem for stem, (_, origin) in THIEN_TRU_BY_YEAR_STEM.items() if origin != "OBSERVED"
)


def place_luu_ha(year_stem: int) -> int:
    """Lưu Hà: tra thẳng bảng theo can năm. Không có công thức để suy ra."""
    return LUU_HA_BY_YEAR_STEM[_stem(year_stem, "can năm")]


def place_thien_tru(year_stem: int) -> int:
    """Thiên Trù: tra thẳng bảng theo can năm. Không có công thức để suy ra.

    **Chín trên mười hàng của bảng này chưa có bằng chứng nào chống lưng** — xem
    ``THIEN_TRU_BY_YEAR_STEM``. Hàm vẫn trả về một vị trí, vì một lá số thiếu hẳn sao
    thì không ai soát được gì; nhưng đừng đọc kết quả này ngang hàng với những sao có
    luật suy ra được.
    """
    branch, _origin = THIEN_TRU_BY_YEAR_STEM[_stem(year_stem, "can năm")]
    return branch


# ------------------------------------------------------------ Giải Thần / Thiên Y


#: Giải Thần theo **cặp tháng âm** — biến thể *không* được chọn. Xem ``place_giai_than``.
_GIAI_THAN_START = CHI.index("Thân")


def place_giai_than_by_month_pair(lunar_month: int) -> int:
    """Biến thể A: 1–2 Thân, 3–4 Tuất, 5–6 Tý, 7–8 Dần, 9–10 Thìn, 11–12 Ngọ.

    **Không phải biến thể đang dùng.** Giữ lại vì nó là một trong hai đường ứng viên
    có thật, và vì bản đối chiếu chỉ loại được nó ở *một* lá số — một điểm dữ liệu
    bác bỏ được một luật, nhưng không xoá nó khỏi lịch sử.
    """
    return (_GIAI_THAN_START + 2 * ((_month(lunar_month) - 1) // 2)) % 12


def place_giai_than(year_branch: int) -> int:
    """Giải Thần: **cung mộ của tam hợp chi năm**.

    Dự án từng đi biến thể theo cặp tháng âm. Bản đối chiếu (13/10/1999 giờ Ngọ, nam)
    đặt Giải Thần ở **Mùi**; biến thể tháng cho **Thìn**, biến thể tam hợp cho **Mùi**.
    Một điểm dữ liệu không chứng minh được luật, nhưng nó **bác bỏ** được một luật, và
    đó là thứ đã xảy ra ở đây.

    **Cảnh báo cho người thẩm định:** luật này trùng hệt luật Hoa Cái, nên Giải Thần
    **luôn đồng cung Hoa Cái**. Hai sao khác nhau mà không bao giờ rời nhau là điều
    đáng soi — hoặc đó là tính chất thật của cặp sao này, hoặc một trong hai luật
    chép nhầm sang cái kia. Bản đối chiếu đặt cả hai ở Mùi nên nó không phân biệt
    được hai khả năng ấy.
    """
    return group2.place_hoa_cai(_branch(year_branch, "chi năm"))


def place_thien_y(lunar_month: int) -> int:
    """Thiên Y: khởi Sửu tháng Giêng, đếm thuận theo tháng âm.

    Lý do chặn cũ là "không nêu lại được luật đáng tin". Cái gỡ được nó là hai cách
    phát biểu **trùng khớp**: một số bản ghi "Thiên Y đồng cung Thiên Riêu", bản khác
    ghi "khởi Sửu tháng Giêng đếm thuận" — mà Thiên Riêu (Thiên Diêu) ở dự án này
    chính là khởi Sửu tháng Giêng đếm thuận. Hai đường độc lập ra cùng một chỗ là
    bằng chứng, không phải mâu thuẫn.

    Hệ quả: Thiên Y **luôn đồng cung Thiên Diêu**. Đó là bất biến để kiểm, và cũng là
    thứ khiến sao này đáng ngờ nhất trong bốn sao vừa gỡ chặn — nếu bản đối chiếu đặt
    nó khác Thiên Diêu thì luật này sai, và chỗ sai lộ ra ngay.
    """
    return place_thien_dieu(lunar_month)
