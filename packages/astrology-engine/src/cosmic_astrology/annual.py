"""Lưu niên — dữ liệu của **một năm xem**, tách hẳn khỏi lá số gốc.

Nguyên tắc xuyên suốt module này: **không chạm vào lá số gốc**. Đổi năm xem không
được làm dịch một ngôi sao bản mệnh nào. Vì thế lưu niên là một object riêng, tính
theo yêu cầu, và *không* được nướng vào `chart_json` đã lưu — một lá số đã lưu
không mang sẵn một năm xem nào.

Phần lớn luật lưu **dùng lại đúng bảng của lá số gốc**, chỉ thay can/chi năm sinh
bằng can/chi năm xem. Chép lại bảng ở đây là tạo ra nguồn sự thật thứ hai, nên
module này gọi thẳng vào ``stars.placement`` và ``stars.placement_malefic``.

Chỉ **hai luật là thật sự mới**: Lưu Văn Xương và Lưu Văn Khúc — chúng đi theo
thiên can năm xem chứ không theo giờ sinh như bản mệnh.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from cosmic_astrology.calendar.sexagenary import CAN, CHI
from cosmic_astrology.chart.model import StarCategory, Transformation, display_priority_for
from cosmic_astrology.chart.types import PALACE_LABELS, PALACE_ORDER, PalaceName
from cosmic_astrology.conventions.policies import RuleId
from cosmic_astrology.conventions.profile import ConventionProfile
from cosmic_astrology.stars import placement, placement_malefic
from cosmic_astrology.stars import placement_group2 as group2
from cosmic_astrology.stars.catalog import definition_for
from cosmic_astrology.stars.four_transformations import transformations_for_stem
from cosmic_astrology.stars.presentation import column_for

__all__ = [
    "ANNUAL_PALACE_SHORT_LABELS",
    "AnnualChart",
    "AnnualPalace",
    "AnnualStar",
    "AnnualTransformation",
    "build_annual_chart",
    "year_pillar",
]

#: Nhãn ngắn của 12 cung lưu niên, như lá số in vẫn ghi ở góc phải mỗi cung.
ANNUAL_PALACE_SHORT_LABELS: Mapping[PalaceName, str] = {
    PalaceName.MENH: "MỆNH",
    PalaceName.PHU_MAU: "PHỤ",
    PalaceName.PHUC_DUC: "PHÚC",
    PalaceName.DIEN_TRACH: "ĐIỀN",
    PalaceName.QUAN_LOC: "QUAN",
    PalaceName.NO_BOC: "NÔ",
    PalaceName.THIEN_DI: "DI",
    PalaceName.TAT_ACH: "TẬT",
    PalaceName.TAI_BACH: "TÀI",
    PalaceName.TU_TUC: "TỬ",
    PalaceName.PHU_THE: "PHỐI",
    PalaceName.HUYNH_DE: "HUYNH",
}


def year_pillar(viewing_year: int) -> tuple[int, int]:
    """Can chi của một năm âm lịch, trả về ``(can_index, chi_index)``.

    Dùng chu kỳ 60 neo tại năm Giáp Tý. Đây là **năm âm lịch**: một ngày dương
    trước Tết thuộc năm âm trước đó, nhưng "năm xem" là một năm tử vi nên công
    thức này đúng với cách người dùng chọn.
    """
    if not 1900 <= viewing_year <= 2100:
        raise ValueError(f"Năm xem phải trong 1900–2100, nhận {viewing_year}")
    return ((viewing_year - 4) % 10, (viewing_year - 4) % 12)


@dataclass(frozen=True, slots=True)
class AnnualPalace:
    """Một cung lưu niên: tên cung nào rơi vào địa chi nào trong năm xem."""

    branch_index: int
    branch: str
    name: PalaceName
    label: str
    short_label: str

    def to_dict(self) -> dict[str, object]:
        return {
            "branch_index": self.branch_index,
            "branch": self.branch,
            "name": self.name.value,
            "label": self.label,
            "short_label": self.short_label,
        }


#: Lưu tinh mà lá số in đối chiếu ghi ra. **Siêu dữ liệu trình bày, không phải luật**
#: — không có phép an sao nào đọc tập này, và mọi lưu tinh vẫn được tính như nhau.
#:
#: Đặt ở engine chứ không ở renderer là có lý do: renderer tuyệt đối không được rẽ
#: nhánh theo mã sao, và có một bài test quét mã nguồn renderer để giữ điều đó. Danh
#: sách này thuộc về nơi biết lá số đối chiếu ghi gì.
TRADITIONAL_DISPLAY_STAR_IDS: frozenset[str] = frozenset(
    {
        "LUU_LOC_TON",
        "LUU_THAI_TUE",
        "LUU_KINH_DUONG",
        "LUU_DA_LA",
        "LUU_THIEN_MA",
        "LUU_TANG_MON",
        "LUU_BACH_HO",
        "LUU_THIEN_KHOC",
        "LUU_THIEN_HU",
    }
)


@dataclass(frozen=True, slots=True)
class AnnualStar:
    """Một lưu tinh.

    ``base_star_id`` trỏ về sao bản mệnh cùng tên khi có, để ngũ hành được **dùng
    lại** chứ không khai báo hai lần: là lưu tinh không làm đổi hành của một ngôi
    sao.
    """

    id: str
    name: str
    base_star_id: str | None
    palace_branch_index: int
    palace_branch: str

    @property
    def traditional_display(self) -> bool:
        """Lá số in đối chiếu có ghi lưu tinh này ra hay không.

        **Chỉ là siêu dữ liệu trình bày.** Nó không tham gia vào bất kỳ phép an sao
        nào; mọi lưu tinh vẫn được tính và vẫn nằm trong ``AnnualChart.stars`` bất kể
        cờ này. Renderer đọc nó để chọn *hiện gì*, và vì thế renderer không cần biết
        mã sao nào — đó là chỗ danh sách này phải nằm.

        Engine an nhiều lưu tinh hơn số bản in ghi ra. Dữ liệu thừa thì cắt được ở
        tầng hiển thị; dữ liệu thiếu thì không.
        """
        return self.id in TRADITIONAL_DISPLAY_STAR_IDS

    @property
    def element(self) -> str | None:
        definition = definition_for(self.base_star_id) if self.base_star_id else None
        return definition.element.value if definition and definition.element else None

    @property
    def polarity(self) -> str | None:
        definition = definition_for(self.base_star_id) if self.base_star_id else None
        return definition.polarity.value if definition and definition.polarity else None

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "base_star_id": self.base_star_id,
            "traditional_display": self.traditional_display,
            # Lưu tinh dùng lại cột của sao gốc: "L.Kình Dương" là Kình Dương của năm
            # xem, và nó không đổi phe vì đổi lớp.
            "traditional_column": column_for(self.id, self.base_star_id).value,
            "category": StarCategory.ANNUAL.value,
            "element": self.element,
            "polarity": self.polarity,
            # Lưu tinh chưa bao giờ mang độ sáng: bảng 168 ô còn rỗng, và kể cả khi
            # có thì nó là bảng của sao bản mệnh.
            "strength": None,
            "is_annual": True,
            "palace_branch": self.palace_branch,
            "palace_branch_index": self.palace_branch_index,
            "display_priority": display_priority_for(StarCategory.ANNUAL),
        }


@dataclass(frozen=True, slots=True)
class AnnualTransformation:
    """Một hóa của năm xem, gắn vào **sao bản mệnh** chứ không sinh sao mới."""

    transformation: Transformation
    star_id: str
    star_name: str

    def to_dict(self) -> dict[str, object]:
        return {
            "transformation": self.transformation.value,
            "short_label": self.transformation.short_label,
            "star_id": self.star_id,
            "star_name": self.star_name,
        }


@dataclass(frozen=True, slots=True)
class AnnualChart:
    """Toàn bộ dữ liệu của một năm xem."""

    viewing_year: int
    year_stem: str
    year_branch: str
    year_pillar_name: str
    #: Tuổi ta và tuổi tròn được nêu **riêng**. Quy ước Nam phái dùng cách nào là
    #: câu hỏi mở Q11, nên engine không chọn hộ — nó đưa cả hai và nói rõ.
    age_tuoi_ta: int | None
    age_completed: int | None
    age_convention: str | None
    palaces: tuple[AnnualPalace, ...]
    stars: tuple[AnnualStar, ...]
    transformations: tuple[AnnualTransformation, ...]
    convention_profile: str
    convention_version: str
    rules: list[dict[str, object]] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "viewing_year": self.viewing_year,
            "year_stem": self.year_stem,
            "year_branch": self.year_branch,
            "year_pillar": self.year_pillar_name,
            "age_tuoi_ta": self.age_tuoi_ta,
            "age_completed": self.age_completed,
            # ``None`` cho tới khi Q11 được trả lời — xem docs/astrology-conventions.md.
            "age_convention": self.age_convention,
            "convention_profile": self.convention_profile,
            "convention_version": self.convention_version,
            "palaces": [p.to_dict() for p in self.palaces],
            "stars": [s.to_dict() for s in self.stars],
            "transformations": [t.to_dict() for t in self.transformations],
            "rules": self.rules,
        }


def _annual_palaces(year_branch: int) -> tuple[AnnualPalace, ...]:
    """12 cung lưu niên: cung Mệnh lưu rơi vào địa chi của năm xem.

    Dùng lại ``PALACE_ORDER`` — cùng trình tự với lá số gốc, chỉ khác điểm khởi.
    Trình tự 12 cung là một, không có bản "lưu niên" riêng.
    """
    return tuple(
        AnnualPalace(
            branch_index=(year_branch + offset) % 12,
            branch=CHI[(year_branch + offset) % 12],
            name=palace_name,
            label=PALACE_LABELS[palace_name],
            short_label=ANNUAL_PALACE_SHORT_LABELS[palace_name],
        )
        for offset, palace_name in enumerate(PALACE_ORDER)
    )


#: Lưu tinh dùng lại đúng bảng của lá số gốc, chỉ thay can/chi. ``(mã, tên, mã gốc)``.
_FROM_YEAR_STEM: tuple[tuple[str, str, str], ...] = (
    ("LUU_LOC_TON", "L.Lộc Tồn", "LOC_TON"),
    ("LUU_THIEN_KHOI", "L.Thiên Khôi", "THIEN_KHOI"),
    ("LUU_THIEN_VIET", "L.Thiên Việt", "THIEN_VIET"),
)

_FROM_YEAR_BRANCH: tuple[tuple[str, str, str], ...] = (
    ("LUU_THIEN_MA", "L.Thiên Mã", "THIEN_MA"),
    ("LUU_DAO_HOA", "L.Đào Hoa", "DAO_HOA"),
    ("LUU_HONG_LOAN", "L.Hồng Loan", "HONG_LOAN"),
    ("LUU_THIEN_HY", "L.Thiên Hỷ", "THIEN_HY"),
    ("LUU_THIEN_KHOC", "L.Thiên Khốc", "THIEN_KHOC"),
    ("LUU_THIEN_HU", "L.Thiên Hư", "THIEN_HU"),
)

#: Bốn sao vòng Thái Tuế mà lá số in vẫn ghi kèm Lưu Thái Tuế. Dùng lại **đúng chu
#: kỳ** của lá số gốc, chỉ neo vào chi năm xem.
_ANNUAL_THAI_TUE: tuple[tuple[str, str, str], ...] = (
    ("LUU_THAI_TUE", "L.Thái Tuế", "THAI_TUE"),
    ("LUU_TANG_MON", "L.Tang Môn", "TANG_MON"),
    ("LUU_QUAN_PHU", "L.Quan Phù", "QUAN_PHU_TT"),
    ("LUU_BACH_HO", "L.Bạch Hổ", "BACH_HO"),
    ("LUU_DIEU_KHACH", "L.Điếu Khách", "DIEU_KHACH"),
)


def place_luu_van_xuong(year_stem: int) -> int:
    """Lưu Văn Xương: cách **Lộc Tồn của can năm xem** 3 cung theo chiều thuận.

    Khác hẳn Văn Xương bản mệnh, vốn an theo **giờ sinh**. Bảng theo can mà các
    sách ghi ra đúng bằng offset cố định này ở cả 10 can.
    """
    return (placement.place_loc_ton(year_stem) + 3) % 12


def place_luu_van_khuc(year_stem: int) -> int:
    """Lưu Văn Khúc: đối xứng với Lưu Văn Xương qua trục Sửu–Mùi.

    Tổng hai vị trí luôn ≡ 2 (mod 12) ở cả 10 can — quan hệ này viết thẳng ra đây
    thay vì chép lại một bảng thứ hai.
    """
    return (2 - place_luu_van_xuong(year_stem)) % 12


def build_annual_chart(
    *,
    viewing_year: int,
    birth_year: int | None,
    profile: ConventionProfile,
) -> AnnualChart:
    """Dữ liệu lưu niên của một năm xem.

    Không nhận và không trả về gì thuộc lá số gốc: hàm này chỉ cần năm xem. Nhờ
    vậy đổi năm xem **không thể** làm dịch một ngôi sao bản mệnh nào — không phải
    vì cẩn thận, mà vì nó không có đường nào chạm tới.
    """
    stem, branch = year_pillar(viewing_year)
    loc_ton = placement.place_loc_ton(stem)

    placed: list[tuple[str, str, str, int]] = []
    for star_id, name, base in _FROM_YEAR_STEM:
        table = {
            "LUU_LOC_TON": loc_ton,
            "LUU_THIEN_KHOI": placement.place_thien_khoi(stem),
            "LUU_THIEN_VIET": placement.place_thien_viet(stem),
        }
        placed.append((star_id, name, base, table[star_id]))

    kinh = placement.place_kinh_duong(loc_ton)
    placed.append(("LUU_KINH_DUONG", "L.Kình Dương", "KINH_DUONG", kinh))
    placed.append(("LUU_DA_LA", "L.Đà La", "DA_LA", placement.place_da_la(loc_ton)))
    placed.append(("LUU_VAN_XUONG", "L.Văn Xương", "VAN_XUONG", place_luu_van_xuong(stem)))
    placed.append(("LUU_VAN_KHUC", "L.Văn Khúc", "VAN_KHUC", place_luu_van_khuc(stem)))

    branch_table = {
        "LUU_THIEN_MA": placement.place_thien_ma(branch),
        "LUU_DAO_HOA": placement.place_dao_hoa(branch),
        "LUU_HONG_LOAN": placement.place_hong_loan(branch),
        "LUU_THIEN_HY": placement.place_thien_hy(branch),
        "LUU_THIEN_KHOC": placement_malefic.place_thien_khoc(branch),
        "LUU_THIEN_HU": placement_malefic.place_thien_hu(branch),
    }
    for star_id, name, base in _FROM_YEAR_BRANCH:
        placed.append((star_id, name, base, branch_table[star_id]))

    for star_id, name, base in _ANNUAL_THAI_TUE:
        placed.append((star_id, name, base, group2.place_thai_tue_member(branch, base)))

    stars = tuple(
        AnnualStar(
            id=star_id,
            name=name,
            base_star_id=base,
            palace_branch_index=at,
            palace_branch=CHI[at],
        )
        for star_id, name, base, at in placed
    )

    def _target_name(star_id: str) -> str:
        definition = definition_for(star_id)
        return definition.vietnamese_name if definition else star_id

    transformations = tuple(
        AnnualTransformation(
            transformation=transformation,
            star_id=target,
            star_name=_target_name(target),
        )
        for transformation, target in transformations_for_stem(stem).items()
    )

    used_rules = (
        RuleId.LOC_TON,
        RuleId.KINH_DUONG_DA_LA,
        RuleId.THIEN_KHOI_THIEN_VIET,
        RuleId.THIEN_MA,
        RuleId.DAO_HOA,
        RuleId.HONG_LOAN_THIEN_HY,
        RuleId.THIEN_KHOC_THIEN_HU,
        RuleId.THAI_TUE_CYCLE,
        RuleId.FOUR_TRANSFORMATIONS,
        RuleId.LUU_VAN_XUONG_VAN_KHUC,
        RuleId.MAJOR_CYCLE_START_AGE,
    )

    return AnnualChart(
        viewing_year=viewing_year,
        year_stem=CAN[stem],
        year_branch=CHI[branch],
        year_pillar_name=f"{CAN[stem]} {CHI[branch]}",
        age_tuoi_ta=None if birth_year is None else viewing_year - birth_year + 1,
        age_completed=None if birth_year is None else viewing_year - birth_year,
        # Quy ước chưa chọn tuổi ta hay tuổi tròn — Q11.
        age_convention=None,
        palaces=_annual_palaces(branch),
        stars=stars,
        transformations=transformations,
        convention_profile=profile.profile_id,
        convention_version=profile.version,
        rules=[profile.binding(rule).to_dict() for rule in used_rules],
    )
