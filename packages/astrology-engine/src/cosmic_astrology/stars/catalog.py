"""The star catalog — what each star *is*, in one place.

Placement lives in ``chart.builder``; this module answers the other question. A
star's ngũ hành, âm/dương, category and display order are properties of the star
itself and do not depend on a birth moment, so they must not be scattered through
the placement algorithms. The chains in ``chart.builder`` carry star **ids** and
offsets only — every name and every attribute is looked up here.

**Why several stars carry no element.** Cosmic Signs has not selected a reference
edition yet (Q1/Q2/Q3 in ``docs/astrology-conventions.md``), so *nothing* in this
catalog is ``VERIFIED``. Where the classical texts are read the same way across
schools, the value is recorded as ``PROVISIONAL`` with its provenance gap stated;
where they genuinely disagree, ``element`` and ``polarity`` are ``None`` and the
star renders in neutral ink. Guessing to complete the table would put a claim on a
customer's chart that no source backs.

Promotion to ``VERIFIED`` happens through the review workflow, never by editing
this file.
"""

from __future__ import annotations

import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType

from cosmic_astrology.calendar.sexagenary import Element
from cosmic_astrology.chart.model import StarCategory, display_priority_for
from cosmic_astrology.conventions.policies import VerificationStatus
from cosmic_astrology.conventions.provenance import SourceReference

__all__ = [
    "STAR_CATALOG",
    "BlankReason",
    "CategoryCoverage",
    "MetadataCoverage",
    "MetadataStatus",
    "Polarity",
    "StarDefinition",
    "canonical_form",
    "definition_for",
    "metadata_coverage",
]


class MetadataStatus(StrEnum):
    """Ba trạng thái của một trường metadata sao, không phải hai."""

    KNOWN = "KNOWN"
    DISPUTED = "DISPUTED"
    NOT_RECORDED = "NOT_RECORDED"


class BlankReason(StrEnum):
    """Vì sao một mục để trống ngũ hành.

    Hai trạng thái này **khác nhau** và gộp chúng lại là đánh mất thông tin: một
    bên là các sách ghi khác nhau (người thẩm định phải *chọn*), bên kia là chưa ai
    tra cứu (người thẩm định phải *tìm*). Việc cần làm tiếp không giống nhau.
    """

    #: Các trường phái ghi khác nhau — phải liệt kê các cách đọc đang mâu thuẫn.
    DISPUTED = "DISPUTED"
    #: Chưa tra được từ nguồn nào. Không phải tranh chấp, chỉ là chưa có.
    NOT_RECORDED = "NOT_RECORDED"


class Polarity(StrEnum):
    """Âm/dương of a star. Rendered as a ``+``/``−`` prefix; never a colour."""

    YANG = "YANG"
    YIN = "YIN"


def canonical_form(name: str) -> str:
    """Diacritic-free spelling of a Vietnamese star name.

    Deterministic text folding, not astrology: it exists so a name can be searched,
    sorted and logged without depending on the reader's keyboard. ``đ`` has no
    combining decomposition, so it is mapped explicitly.
    """
    folded = name.replace("đ", "d").replace("Đ", "D")
    decomposed = unicodedata.normalize("NFD", folded)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


#: Every entry in this catalog until a reference edition is chosen. Being explicit
#: beats leaving the field empty: it records *why* nothing is cited.
_NO_REFERENCE_SELECTED = SourceReference(
    note=(
        "Chưa chọn ấn bản chuẩn (Q1/Q2/Q3). Giá trị dưới đây ghi theo chỗ các bản "
        "đọc trùng nhau, KHÔNG phải trích từ một nguồn đã chốt — xem "
        "docs/astrology-conventions.md mục 23."
    )
)


@dataclass(frozen=True, slots=True)
class StarDefinition:
    """One star's identity and attributes, with the standing of each claim attached.

    ``element`` and ``polarity`` move together: the classical sources state them as
    a single phrase ("âm thủy"), so when that phrase is disputed neither half is
    recorded and ``verification_status`` drops to ``UNVERIFIED``.
    """

    id: str
    #: Diacritic-free spelling, for search, sorting and logs.
    canonical_name: str
    #: Display name with diacritics. The only name a reader should see.
    vietnamese_name: str
    category: StarCategory
    element: Element | None
    polarity: Polarity | None
    #: Trust in this star's *metadata* — separate from trust in its placement,
    #: which belongs to the convention rule that placed it.
    verification_status: VerificationStatus
    provenance: SourceReference
    #: Why this reading was recorded, or why nothing was.
    note: str
    #: Competing readings found in other schools. Never silently merged.
    alternatives: tuple[str, ...] = field(default_factory=tuple)
    #: Vì sao ``element`` để trống. Bắt buộc khi để trống, cấm khi đã có giá trị.
    blank_reason: BlankReason | None = None

    def __post_init__(self) -> None:
        if (self.element is None) != (self.polarity is None):
            raise ValueError(
                f"{self.vietnamese_name}: ngũ hành và âm/dương phải cùng có hoặc cùng "
                "thiếu — chúng đến từ cùng một câu trong sách."
            )
        if not self.note.strip():
            raise ValueError(
                f"{self.vietnamese_name}: phải ghi lý do cho giá trị (hoặc cho việc để trống)."
            )
        if self.element is None and self.blank_reason is None:
            raise ValueError(
                f"{self.vietnamese_name}: để trống ngũ hành thì phải nói RÕ vì sao — "
                "tranh chấp giữa các sách, hay chưa tra cứu được."
            )
        if self.blank_reason is BlankReason.DISPUTED and len(self.alternatives) < 2:
            raise ValueError(
                f"{self.vietnamese_name}: đã nói là tranh chấp thì phải liệt kê các cách "
                "đọc đang mâu thuẫn, nếu không thì đó là im lặng chứ không phải ghi nhận."
            )
        if self.element is not None and self.blank_reason is not None:
            raise ValueError(f"{self.vietnamese_name}: đã có ngũ hành thì không có lý do trống.")
        if self.element is None and self.verification_status is not VerificationStatus.UNVERIFIED:
            raise ValueError(
                f"{self.vietnamese_name}: không có ngũ hành thì không thể là "
                f"{self.verification_status.value}."
            )
        if self.verification_status is VerificationStatus.VERIFIED and not (
            self.provenance.is_complete
        ):
            raise ValueError(
                f"{self.vietnamese_name}: chỉ được VERIFIED khi provenance có cả trích dẫn "
                "và người ký duyệt."
            )
        if self.canonical_name != canonical_form(self.vietnamese_name):
            raise ValueError(
                f"{self.vietnamese_name}: canonical_name phải là dạng bỏ dấu của tên tiếng Việt."
            )

    @property
    def element_status(self) -> MetadataStatus:
        """KNOWN / DISPUTED / NOT_RECORDED — trạng thái ngũ hành của sao này.

        Ba trạng thái dẫn tới ba việc khác nhau: dùng được ngay, phải **chọn**, hay
        phải **tìm**. Gộp chúng thành "có/không" là đánh mất điều đó.
        """
        if self.element is not None:
            return MetadataStatus.KNOWN
        return (
            MetadataStatus.DISPUTED
            if self.blank_reason is BlankReason.DISPUTED
            else MetadataStatus.NOT_RECORDED
        )

    @property
    def polarity_status(self) -> MetadataStatus:
        """Trạng thái âm/dương.

        Luôn bằng ``element_status``: sách ghi hai thứ này trong cùng một câu
        ("âm thủy"), nên bất biến của catalog buộc chúng cùng có hoặc cùng thiếu.
        """
        return MetadataStatus.KNOWN if self.polarity is not None else self.element_status

    @property
    def has_element(self) -> bool:
        return self.element is not None

    @property
    def has_polarity(self) -> bool:
        return self.polarity is not None

    @property
    def display_priority(self) -> int:
        return display_priority_for(self.category)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "canonical_name": self.canonical_name,
            "vietnamese_name": self.vietnamese_name,
            "category": self.category.value,
            "element": self.element.value if self.element else None,
            "polarity": self.polarity.value if self.polarity else None,
            "display_priority": self.display_priority,
            "verification_status": self.verification_status.value,
            "provenance": self.provenance.to_dict(),
            "note": self.note,
            "alternatives": list(self.alternatives),
            "blank_reason": self.blank_reason.value if self.blank_reason else None,
        }


def _major(
    star_id: str,
    vietnamese_name: str,
    element: Element | None,
    polarity: Polarity | None,
    note: str,
    alternatives: tuple[str, ...] = (),
    blank_reason: BlankReason | None = None,
) -> StarDefinition:
    return StarDefinition(
        id=star_id,
        canonical_name=canonical_form(vietnamese_name),
        vietnamese_name=vietnamese_name,
        category=StarCategory.MAJOR,
        element=element,
        polarity=polarity,
        # A recorded value is PROVISIONAL at best while no edition is selected;
        # a blank one has nothing to be provisional about.
        verification_status=(
            VerificationStatus.PROVISIONAL if element else VerificationStatus.UNVERIFIED
        ),
        provenance=_NO_REFERENCE_SELECTED,
        note=note,
        alternatives=alternatives,
        blank_reason=blank_reason,
    )


def _minor(
    star_id: str,
    vietnamese_name: str,
    category: StarCategory,
    element: Element | None,
    polarity: Polarity | None,
    note: str,
    alternatives: tuple[str, ...] = (),
    blank_reason: BlankReason | None = None,
) -> StarDefinition:
    """A phụ tinh. Same standing as a chính tinh: recorded, never verified yet."""
    return StarDefinition(
        id=star_id,
        canonical_name=canonical_form(vietnamese_name),
        vietnamese_name=vietnamese_name,
        category=category,
        element=element,
        polarity=polarity,
        verification_status=(
            VerificationStatus.PROVISIONAL if element else VerificationStatus.UNVERIFIED
        ),
        provenance=_NO_REFERENCE_SELECTED,
        note=note,
        alternatives=alternatives,
        blank_reason=blank_reason,
    )


#: The 14 chính tinh. Ids are the placement chains' only reference to a star.
_DEFINITIONS: tuple[StarDefinition, ...] = (
    _major("TU_VI", "Tử Vi", Element.THO, Polarity.YIN, "Âm thổ — nhất quán giữa các sách."),
    _major("THIEN_CO", "Thiên Cơ", Element.MOC, Polarity.YIN, "Âm mộc — nhất quán."),
    _major("THAI_DUONG", "Thái Dương", Element.HOA, Polarity.YANG, "Dương hỏa — nhất quán."),
    _major("VU_KHUC", "Vũ Khúc", Element.KIM, Polarity.YIN, "Âm kim — nhất quán."),
    _major("THIEN_DONG", "Thiên Đồng", Element.THUY, Polarity.YANG, "Dương thủy — nhất quán."),
    _major(
        "LIEM_TRINH",
        "Liêm Trinh",
        Element.KIM,
        Polarity.YIN,
        "Âm kim — đa số sách Đẩu Số ghi vậy (hóa khí là tù).",
        ("Một số bản Việt ghi Hỏa; cần bản in cụ thể để chốt.",),
    ),
    _major("THIEN_PHU", "Thiên Phủ", Element.THO, Polarity.YANG, "Dương thổ — nhất quán."),
    _major("THAI_AM", "Thái Âm", Element.THUY, Polarity.YIN, "Âm thủy — nhất quán."),
    _major(
        "THAM_LANG",
        "Tham Lang",
        None,
        None,
        "CHƯA GHI NHẬN. Sách cổ ghi 'âm thủy, hóa khí là mộc' — hai hành trong cùng "
        "một câu, nên không có một đáp án đơn trị để tô màu.",
        ("Thủy (bản thể)", "Mộc (hóa khí)"),
        BlankReason.DISPUTED,
    ),
    _major(
        "CU_MON",
        "Cự Môn",
        None,
        None,
        "CHƯA GHI NHẬN. Các trường phái ghi khác nhau rõ rệt, chưa có nguồn chuẩn để chọn.",
        ("Thổ (đa số bản Hoa)", "Thủy (một số bản Việt)", "Kim (thiểu số)"),
        BlankReason.DISPUTED,
    ),
    _major("THIEN_TUONG", "Thiên Tướng", Element.THUY, Polarity.YANG, "Dương thủy — nhất quán."),
    _major(
        "THIEN_LUONG",
        "Thiên Lương",
        Element.THO,
        Polarity.YANG,
        "Dương thổ — đa số sách ghi vậy.",
        ("Một số bản suy từ chữ 梁 (rường gỗ) mà ghi Mộc.",),
    ),
    _major("THAT_SAT", "Thất Sát", Element.KIM, Polarity.YANG, "Dương kim — nhất quán."),
    _major("PHA_QUAN", "Phá Quân", Element.THUY, Polarity.YIN, "Âm thủy — nhất quán."),
)

#: Phụ tinh nhóm 1 — an theo Nam phái, xem ``stars/placement.py``.
_SUPPORTING_GROUP_1: tuple[StarDefinition, ...] = (
    _minor(
        "VAN_XUONG",
        "Văn Xương",
        StarCategory.LITERARY,
        Element.KIM,
        Polarity.YANG,
        "Dương kim — nhất quán giữa các sách.",
    ),
    _minor(
        "VAN_KHUC",
        "Văn Khúc",
        StarCategory.LITERARY,
        Element.THUY,
        Polarity.YIN,
        "Âm thủy — nhất quán.",
    ),
    _minor(
        "TA_PHU",
        "Tả Phù",
        StarCategory.SUPPORTING,
        Element.THO,
        Polarity.YANG,
        "Dương thổ — nhất quán.",
    ),
    _minor(
        "HUU_BAT",
        "Hữu Bật",
        StarCategory.SUPPORTING,
        None,
        None,
        "CHƯA GHI NHẬN. Tả Phù thì các sách thống nhất là Thổ, nhưng Hữu Bật thì "
        "không — đủ khác nhau để không chọn bừa một bên.",
        ("Thổ (đi theo Tả Phù, phần lớn bản Việt)", "Thủy (phần lớn bản Hoa: 右弼 屬水)"),
        BlankReason.DISPUTED,
    ),
    _minor(
        "THIEN_KHOI",
        "Thiên Khôi",
        StarCategory.SUPPORTING,
        Element.HOA,
        Polarity.YANG,
        "Dương hỏa — nhất quán.",
    ),
    _minor(
        "THIEN_VIET",
        "Thiên Việt",
        StarCategory.SUPPORTING,
        Element.HOA,
        Polarity.YIN,
        "Âm hỏa — nhất quán.",
    ),
    _minor(
        "LOC_TON",
        "Lộc Tồn",
        StarCategory.WEALTH,
        Element.THO,
        Polarity.YIN,
        "Âm thổ — nhất quán.",
    ),
    _minor(
        "KINH_DUONG",
        "Kình Dương",
        StarCategory.MALEFIC,
        Element.KIM,
        Polarity.YANG,
        "Dương kim — nhất quán.",
    ),
    _minor(
        "DA_LA",
        "Đà La",
        StarCategory.MALEFIC,
        Element.KIM,
        Polarity.YIN,
        "Âm kim — nhất quán.",
    ),
    _minor(
        "DAO_HOA",
        "Đào Hoa",
        StarCategory.ROMANCE,
        None,
        None,
        "CHƯA GHI NHẬN. Các sách chia hai hướng rõ rệt, chưa có nguồn chuẩn để chọn.",
        ("Mộc (một số bản Việt)", "Thủy (Hàm Trì 咸池 thuộc thủy, phần lớn bản Hoa)"),
        BlankReason.DISPUTED,
    ),
    _minor(
        "HONG_LOAN",
        "Hồng Loan",
        StarCategory.ROMANCE,
        Element.THUY,
        Polarity.YIN,
        "Âm thủy — nhất quán.",
    ),
    _minor(
        "THIEN_HY",
        "Thiên Hỷ",
        StarCategory.ROMANCE,
        Element.THUY,
        Polarity.YANG,
        "Dương thủy — nhất quán.",
    ),
    _minor(
        "THIEN_MA",
        "Thiên Mã",
        StarCategory.SUPPORTING,
        Element.HOA,
        Polarity.YANG,
        "Dương hỏa — nhất quán.",
    ),
)

#: Phụ tinh nhóm 2 — an theo Nam phái, xem ``stars/placement_group2.py``.
#: Ngũ hành của cả nhóm hiện để TRỐNG: chưa tra được từ nguồn nào. Đó là
#: NOT_RECORDED, khác với DISPUTED của Tham Lang / Cự Môn / Hữu Bật / Đào Hoa.
_SUPPORTING_GROUP_2: tuple[StarDefinition, ...] = (
    _minor(
        "LONG_TRI",
        "Long Trì",
        StarCategory.NOBILITY,
        Element.THUY,
        Polarity.YANG,
        "Ngũ hành và âm dương theo cách đọc chung của Nam phái. CHƯA đối chiếu ấn "
        "bản nào, nên PROVISIONAL — đúng hạng dữ liệu đã từng sai một lần trong dự "
        "án (hàng Kỷ của bảng Thiên Trù). Điền được vì cặp sao này nêu lại được CẢ "
        "HAI nửa của câu; những sao chỉ nhớ được nửa hành thì để trống.",
    ),
    _minor(
        "PHUONG_CAC",
        "Phượng Các",
        StarCategory.NOBILITY,
        Element.THO,
        Polarity.YIN,
        "Ngũ hành và âm dương theo cách đọc chung của Nam phái. CHƯA đối chiếu ấn "
        "bản nào, nên PROVISIONAL — đúng hạng dữ liệu đã từng sai một lần trong dự "
        "án (hàng Kỷ của bảng Thiên Trù). Điền được vì cặp sao này nêu lại được CẢ "
        "HAI nửa của câu; những sao chỉ nhớ được nửa hành thì để trống.",
    ),
    _minor(
        "TAM_THAI",
        "Tam Thai",
        StarCategory.NOBILITY,
        Element.THO,
        Polarity.YANG,
        "Ngũ hành và âm dương theo cách đọc chung của Nam phái. CHƯA đối chiếu ấn "
        "bản nào, nên PROVISIONAL — đúng hạng dữ liệu đã từng sai một lần trong dự "
        "án (hàng Kỷ của bảng Thiên Trù). Điền được vì cặp sao này nêu lại được CẢ "
        "HAI nửa của câu; những sao chỉ nhớ được nửa hành thì để trống.",
    ),
    _minor(
        "BAT_TOA",
        "Bát Tọa",
        StarCategory.NOBILITY,
        Element.THO,
        Polarity.YIN,
        "Ngũ hành và âm dương theo cách đọc chung của Nam phái. CHƯA đối chiếu ấn "
        "bản nào, nên PROVISIONAL — đúng hạng dữ liệu đã từng sai một lần trong dự "
        "án (hàng Kỷ của bảng Thiên Trù). Điền được vì cặp sao này nêu lại được CẢ "
        "HAI nửa của câu; những sao chỉ nhớ được nửa hành thì để trống.",
    ),
    _minor(
        "AN_QUANG",
        "Ân Quang",
        StarCategory.NOBILITY,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "THIEN_QUY",
        "Thiên Quý",
        StarCategory.NOBILITY,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "GIAI_THAN",
        "Giải Thần",
        StarCategory.BLESSING,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "THIEN_TRU",
        "Thiên Trù",
        StarCategory.BLESSING,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "THIEN_Y",
        "Thiên Y",
        StarCategory.BLESSING,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "LUU_HA",
        "Lưu Hà",
        StarCategory.MALEFIC,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "THIEN_DUC",
        "Thiên Đức",
        StarCategory.BLESSING,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "NGUYET_DUC",
        "Nguyệt Đức",
        StarCategory.BLESSING,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "LONG_DUC",
        "Long Đức",
        StarCategory.BLESSING,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "PHUC_DUC_STAR",
        "Phúc Đức",
        StarCategory.BLESSING,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "THIEU_DUONG",
        "Thiếu Dương",
        StarCategory.OTHER,
        Element.HOA,
        Polarity.YANG,
        "Ngũ hành và âm dương theo cách đọc chung của Nam phái. CHƯA đối chiếu ấn "
        "bản nào, nên PROVISIONAL — đúng hạng dữ liệu đã từng sai một lần trong dự "
        "án (hàng Kỷ của bảng Thiên Trù). Điền được vì cặp sao này nêu lại được CẢ "
        "HAI nửa của câu; những sao chỉ nhớ được nửa hành thì để trống.",
    ),
    _minor(
        "THIEU_AM",
        "Thiếu Âm",
        StarCategory.OTHER,
        Element.THUY,
        Polarity.YIN,
        "Ngũ hành và âm dương theo cách đọc chung của Nam phái. CHƯA đối chiếu ấn "
        "bản nào, nên PROVISIONAL — đúng hạng dữ liệu đã từng sai một lần trong dự "
        "án (hàng Kỷ của bảng Thiên Trù). Điền được vì cặp sao này nêu lại được CẢ "
        "HAI nửa của câu; những sao chỉ nhớ được nửa hành thì để trống.",
    ),
    _minor(
        "HOA_CAI",
        "Hoa Cái",
        StarCategory.OTHER,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "THIEN_TAI",
        "Thiên Tài",
        StarCategory.SUPPORTING,
        Element.THO,
        Polarity.YANG,
        "Ngũ hành và âm dương theo cách đọc chung của Nam phái. CHƯA đối chiếu ấn "
        "bản nào, nên PROVISIONAL — đúng hạng dữ liệu đã từng sai một lần trong dự "
        "án (hàng Kỷ của bảng Thiên Trù). Điền được vì cặp sao này nêu lại được CẢ "
        "HAI nửa của câu; những sao chỉ nhớ được nửa hành thì để trống.",
    ),
    _minor(
        "THIEN_THO",
        "Thiên Thọ",
        StarCategory.SUPPORTING,
        Element.THO,
        Polarity.YIN,
        "Ngũ hành và âm dương theo cách đọc chung của Nam phái. CHƯA đối chiếu ấn "
        "bản nào, nên PROVISIONAL — đúng hạng dữ liệu đã từng sai một lần trong dự "
        "án (hàng Kỷ của bảng Thiên Trù). Điền được vì cặp sao này nêu lại được CẢ "
        "HAI nửa của câu; những sao chỉ nhớ được nửa hành thì để trống.",
    ),
)

#: Phụ tinh nhóm 2 — phần bổ sung. Ngũ hành cả nhóm vẫn NOT_RECORDED.
_SUPPORTING_GROUP_2B: tuple[StarDefinition, ...] = (
    _minor(
        "THIEN_QUAN",
        "Thiên Quan",
        StarCategory.NOBILITY,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "THIEN_PHUC",
        "Thiên Phúc",
        StarCategory.BLESSING,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "THIEN_GIAI",
        "Thiên Giải",
        StarCategory.BLESSING,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "DIA_GIAI",
        "Địa Giải",
        StarCategory.BLESSING,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "THAI_PHU",
        "Thai Phụ",
        StarCategory.NOBILITY,
        Element.THO,
        Polarity.YANG,
        "Ngũ hành và âm dương theo cách đọc chung của Nam phái. CHƯA đối chiếu ấn "
        "bản nào, nên PROVISIONAL — đúng hạng dữ liệu đã từng sai một lần trong dự "
        "án (hàng Kỷ của bảng Thiên Trù). Điền được vì cặp sao này nêu lại được CẢ "
        "HAI nửa của câu; những sao chỉ nhớ được nửa hành thì để trống.",
    ),
    _minor(
        "PHONG_CAO",
        "Phong Cáo",
        StarCategory.NOBILITY,
        Element.THO,
        Polarity.YIN,
        "Ngũ hành và âm dương theo cách đọc chung của Nam phái. CHƯA đối chiếu ấn "
        "bản nào, nên PROVISIONAL — đúng hạng dữ liệu đã từng sai một lần trong dự "
        "án (hàng Kỷ của bảng Thiên Trù). Điền được vì cặp sao này nêu lại được CẢ "
        "HAI nửa của câu; những sao chỉ nhớ được nửa hành thì để trống.",
    ),
    _minor(
        "QUOC_AN",
        "Quốc Ấn",
        StarCategory.AUTHORITY,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "DUONG_PHU",
        "Đường Phù",
        StarCategory.AUTHORITY,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "HY_THAN",
        "Hỷ Thần",
        StarCategory.BLESSING,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
)

#: Sát tinh / bại tinh nhóm 1. Ngũ hành chỉ ghi nhận ở Hỏa Tinh và Linh Tinh —
#: hai sao mà tên đã nói ra hành. Các sao còn lại để trống: màu trên lá số là
#: NGŨ HÀNH, không phải "tốt hay xấu", nên không được tô đỏ chỉ vì là hung tinh.
_MALEFIC_GROUP_1: tuple[StarDefinition, ...] = (
    _minor(
        "HOA_TINH",
        "Hỏa Tinh",
        StarCategory.MALEFIC,
        Element.HOA,
        Polarity.YANG,
        "Dương hỏa — nhất quán, và chính tên sao đã nói ra hành của nó.",
    ),
    _minor(
        "LINH_TINH",
        "Linh Tinh",
        StarCategory.MALEFIC,
        Element.HOA,
        Polarity.YIN,
        "Âm hỏa — nhất quán.",
    ),
    _minor(
        "DIA_KHONG",
        "Địa Không",
        StarCategory.VOID,
        Element.HOA,
        Polarity.YIN,
        "Ngũ hành và âm dương theo cách đọc chung của Nam phái. CHƯA đối chiếu ấn "
        "bản nào, nên PROVISIONAL — đúng hạng dữ liệu đã từng sai một lần trong dự "
        "án (hàng Kỷ của bảng Thiên Trù). Điền được vì cặp sao này nêu lại được CẢ "
        "HAI nửa của câu; những sao chỉ nhớ được nửa hành thì để trống.",
    ),
    _minor(
        "DIA_KIEP",
        "Địa Kiếp",
        StarCategory.VOID,
        Element.HOA,
        Polarity.YANG,
        "Ngũ hành và âm dương theo cách đọc chung của Nam phái. CHƯA đối chiếu ấn "
        "bản nào, nên PROVISIONAL — đúng hạng dữ liệu đã từng sai một lần trong dự "
        "án (hàng Kỷ của bảng Thiên Trù). Điền được vì cặp sao này nêu lại được CẢ "
        "HAI nửa của câu; những sao chỉ nhớ được nửa hành thì để trống.",
    ),
    _minor(
        "THIEN_KHONG",
        "Thiên Không",
        StarCategory.VOID,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "DAI_HAO",
        "Đại Hao",
        StarCategory.LOSS,
        Element.HOA,
        Polarity.YANG,
        "Ngũ hành và âm dương theo cách đọc chung của Nam phái. CHƯA đối chiếu ấn "
        "bản nào, nên PROVISIONAL — đúng hạng dữ liệu đã từng sai một lần trong dự "
        "án (hàng Kỷ của bảng Thiên Trù). Điền được vì cặp sao này nêu lại được CẢ "
        "HAI nửa của câu; những sao chỉ nhớ được nửa hành thì để trống.",
    ),
    _minor(
        "TIEU_HAO",
        "Tiểu Hao",
        StarCategory.LOSS,
        Element.HOA,
        Polarity.YIN,
        "Ngũ hành và âm dương theo cách đọc chung của Nam phái. CHƯA đối chiếu ấn "
        "bản nào, nên PROVISIONAL — đúng hạng dữ liệu đã từng sai một lần trong dự "
        "án (hàng Kỷ của bảng Thiên Trù). Điền được vì cặp sao này nêu lại được CẢ "
        "HAI nửa của câu; những sao chỉ nhớ được nửa hành thì để trống.",
    ),
    _minor(
        "TANG_MON",
        "Tang Môn",
        StarCategory.MOURNING,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "BACH_HO",
        "Bạch Hổ",
        StarCategory.MOURNING,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "THIEN_KHOC",
        "Thiên Khốc",
        StarCategory.MOURNING,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "THIEN_HU",
        "Thiên Hư",
        StarCategory.MOURNING,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "QUAN_PHU_TT",
        "Quan Phù",
        StarCategory.LEGAL,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "DIEU_KHACH",
        "Điếu Khách",
        StarCategory.LEGAL,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "KIEP_SAT",
        "Kiếp Sát",
        StarCategory.MALEFIC,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "CO_THAN",
        "Cô Thần",
        StarCategory.ISOLATION,
        Element.HOA,
        Polarity.YANG,
        "Ngũ hành và âm dương theo cách đọc chung của Nam phái. CHƯA đối chiếu ấn "
        "bản nào, nên PROVISIONAL — đúng hạng dữ liệu đã từng sai một lần trong dự "
        "án (hàng Kỷ của bảng Thiên Trù). Điền được vì cặp sao này nêu lại được CẢ "
        "HAI nửa của câu; những sao chỉ nhớ được nửa hành thì để trống.",
    ),
    _minor(
        "QUA_TU",
        "Quả Tú",
        StarCategory.ISOLATION,
        Element.HOA,
        Polarity.YIN,
        "Ngũ hành và âm dương theo cách đọc chung của Nam phái. CHƯA đối chiếu ấn "
        "bản nào, nên PROVISIONAL — đúng hạng dữ liệu đã từng sai một lần trong dự "
        "án (hàng Kỷ của bảng Thiên Trù). Điền được vì cặp sao này nêu lại được CẢ "
        "HAI nửa của câu; những sao chỉ nhớ được nửa hành thì để trống.",
    ),
)

#: Phụ tinh nhóm 3. Chín sao đầu hoàn tất vòng Bác Sĩ, hai sao tiếp hoàn tất
#: phần vòng Thái Tuế nhóm này cần — cả hai chu kỳ vẫn chỉ có MỘT nguồn tính.
#: "Quan Phủ" (vòng Bác Sĩ) khác "Quan Phù" (vòng Thái Tuế) — hai sao, hai chữ.
_SUPPORTING_GROUP_3: tuple[StarDefinition, ...] = (
    _minor(
        "BAC_SI",
        "Bác Sĩ",
        StarCategory.OTHER,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "LUC_SI",
        "Lực Sĩ",
        StarCategory.OTHER,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "THANH_LONG",
        "Thanh Long",
        StarCategory.OTHER,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "TUONG_QUAN",
        "Tướng Quân",
        StarCategory.OTHER,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "TAU_THU",
        "Tấu Thư",
        StarCategory.OTHER,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "PHI_LIEM",
        "Phi Liêm",
        StarCategory.OTHER,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "BENH_PHU",
        "Bệnh Phù",
        StarCategory.MOURNING,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "PHUC_BINH",
        "Phục Binh",
        StarCategory.MALEFIC,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "QUAN_PHU_BS",
        "Quan Phủ",
        StarCategory.LEGAL,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    # Hai sao này KHÔNG nằm trong danh sách yêu cầu, nhưng đi trọn vòng Thái Tuế thì
    # chúng được an — và chúng là sao thật, có trên mọi lá số. Bỏ qua chỉ vì không
    # được nhắc tên sẽ để lại hai ô trống khó giải thích.
    _minor(
        "THAI_TUE",
        "Thái Tuế",
        StarCategory.OTHER,
        Element.HOA,
        Polarity.YANG,
        "Ngũ hành và âm dương theo cách đọc chung của Nam phái. CHƯA đối chiếu ấn "
        "bản nào, nên PROVISIONAL — đúng hạng dữ liệu đã từng sai một lần trong dự "
        "án (hàng Kỷ của bảng Thiên Trù). Điền được vì cặp sao này nêu lại được CẢ "
        "HAI nửa của câu; những sao chỉ nhớ được nửa hành thì để trống.",
    ),
    _minor(
        "TUE_PHA",
        "Tuế Phá",
        StarCategory.MALEFIC,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "TU_PHU",
        "Tử Phù",
        StarCategory.MOURNING,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "TRUC_PHU",
        "Trực Phù",
        StarCategory.LEGAL,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "PHA_TOAI",
        "Phá Toái",
        StarCategory.MALEFIC,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "THIEN_HINH",
        "Thiên Hình",
        StarCategory.MALEFIC,
        Element.HOA,
        Polarity.YANG,
        "Ngũ hành và âm dương theo cách đọc chung của Nam phái. CHƯA đối chiếu ấn "
        "bản nào, nên PROVISIONAL — đúng hạng dữ liệu đã từng sai một lần trong dự "
        "án (hàng Kỷ của bảng Thiên Trù). Điền được vì cặp sao này nêu lại được CẢ "
        "HAI nửa của câu; những sao chỉ nhớ được nửa hành thì để trống.",
    ),
    _minor(
        "THIEN_DIEU",
        "Thiên Diêu",
        StarCategory.ROMANCE,
        Element.THUY,
        Polarity.YIN,
        "Ngũ hành và âm dương theo cách đọc chung của Nam phái. CHƯA đối chiếu ấn "
        "bản nào, nên PROVISIONAL — đúng hạng dữ liệu đã từng sai một lần trong dự "
        "án (hàng Kỷ của bảng Thiên Trù). Điền được vì cặp sao này nêu lại được CẢ "
        "HAI nửa của câu; những sao chỉ nhớ được nửa hành thì để trống.",
    ),
    _minor(
        "THIEN_LA",
        "Thiên La",
        StarCategory.MALEFIC,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "DIA_VONG",
        "Địa Võng",
        StarCategory.MALEFIC,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
    _minor(
        "THIEN_THUONG",
        "Thiên Thương",
        StarCategory.MALEFIC,
        Element.THUY,
        Polarity.YANG,
        "Ngũ hành và âm dương theo cách đọc chung của Nam phái. CHƯA đối chiếu ấn "
        "bản nào, nên PROVISIONAL — đúng hạng dữ liệu đã từng sai một lần trong dự "
        "án (hàng Kỷ của bảng Thiên Trù). Điền được vì cặp sao này nêu lại được CẢ "
        "HAI nửa của câu; những sao chỉ nhớ được nửa hành thì để trống.",
    ),
    _minor(
        "THIEN_SU",
        "Thiên Sứ",
        StarCategory.MALEFIC,
        Element.THUY,
        Polarity.YIN,
        "Ngũ hành và âm dương theo cách đọc chung của Nam phái. CHƯA đối chiếu ấn "
        "bản nào, nên PROVISIONAL — đúng hạng dữ liệu đã từng sai một lần trong dự "
        "án (hàng Kỷ của bảng Thiên Trù). Điền được vì cặp sao này nêu lại được CẢ "
        "HAI nửa của câu; những sao chỉ nhớ được nửa hành thì để trống.",
    ),
    _minor(
        "DAU_QUAN",
        "Đẩu Quân",
        StarCategory.OTHER,
        None,
        None,
        "CHƯA TRA CỨU. Ngũ hành của sao này chưa tra được từ nguồn nào — khác với "
        "trường hợp các sách ghi mâu thuẫn. Vẽ bằng mực trung tính.",
        blank_reason=BlankReason.NOT_RECORDED,
    ),
)

#: Read-only so no caller can add a star at runtime.
STAR_CATALOG: Mapping[str, StarDefinition] = MappingProxyType(
    {
        d.id: d
        for d in (
            *_DEFINITIONS,
            *_SUPPORTING_GROUP_1,
            *_SUPPORTING_GROUP_2,
            *_SUPPORTING_GROUP_2B,
            *_MALEFIC_GROUP_1,
            *_SUPPORTING_GROUP_3,
        )
    }
)


def definition_for(star_id: str) -> StarDefinition | None:
    """Catalog entry for a star id, or ``None`` when the star is not catalogued.

    ``None`` is a normal answer, not a failure: every future star will exist in a
    placement rule before anyone has recorded what it is.
    """
    return STAR_CATALOG.get(star_id)


@dataclass(frozen=True, slots=True)
class CategoryCoverage:
    """How much of one category carries metadata. Counted, never estimated."""

    category: StarCategory
    total: int
    with_element: int
    with_polarity: int
    missing_element: tuple[str, ...]
    missing_polarity: tuple[str, ...]
    without_citation: tuple[str, ...]

    @staticmethod
    def _percent(part: int, whole: int) -> float:
        return 0.0 if whole == 0 else round(part / whole * 100, 1)

    @property
    def element_percentage(self) -> float:
        return self._percent(self.with_element, self.total)

    @property
    def polarity_percentage(self) -> float:
        return self._percent(self.with_polarity, self.total)

    def to_dict(self) -> dict[str, object]:
        return {
            "category": self.category.value,
            "total": self.total,
            "with_element": self.with_element,
            "with_polarity": self.with_polarity,
            "element_percentage": self.element_percentage,
            "polarity_percentage": self.polarity_percentage,
            "missing_element": list(self.missing_element),
            "missing_polarity": list(self.missing_polarity),
            "without_citation": list(self.without_citation),
        }


@dataclass(frozen=True, slots=True)
class MetadataCoverage:
    """Catalog coverage, one row per category, in the taxonomy's own order."""

    categories: tuple[CategoryCoverage, ...]

    @property
    def total(self) -> int:
        return sum(c.total for c in self.categories)

    def by_category(self, category: StarCategory) -> CategoryCoverage:
        for row in self.categories:
            if row.category is category:
                return row
        return CategoryCoverage(category, 0, 0, 0, (), (), ())

    def to_dict(self) -> dict[str, object]:
        return {
            "total": self.total,
            "categories": [c.to_dict() for c in self.categories],
        }


def metadata_coverage() -> MetadataCoverage:
    """Coverage counted from the catalog itself, so the report cannot drift."""
    rows: list[CategoryCoverage] = []
    for category in StarCategory:
        entries = [d for d in STAR_CATALOG.values() if d.category is category]
        rows.append(
            CategoryCoverage(
                category=category,
                total=len(entries),
                with_element=sum(1 for d in entries if d.has_element),
                with_polarity=sum(1 for d in entries if d.has_polarity),
                missing_element=tuple(d.vietnamese_name for d in entries if not d.has_element),
                missing_polarity=tuple(d.vietnamese_name for d in entries if not d.has_polarity),
                without_citation=tuple(
                    d.vietnamese_name for d in entries if not d.provenance.has_citation
                ),
            )
        )
    return MetadataCoverage(tuple(rows))
