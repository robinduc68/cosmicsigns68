"""COSMIC_SIGNS_NAM_PHAI_V1 — hồ sơ quy ước Nam phái.

Khác hồ sơ chuẩn đúng một điều: nó **nêu tên trường phái**. Nhờ vậy nó chọn được
luật an cho nhóm phụ tinh 1, thứ mà một hồ sơ không nêu trường phái không có cơ sở
để chọn.

Mọi luật ở đây là **`PROVISIONAL`**. Cosmic Signs vẫn chưa chốt ấn bản chuẩn
(Q1/Q2/Q3), nên "Nam phái" hiện là cách đọc thông dụng chứ chưa phải một trích dẫn.
Nói rõ điều đó ở từng `note` còn hơn để người đọc tưởng đã có sách chống lưng.

Hồ sơ kế thừa toàn bộ ràng buộc của hồ sơ chuẩn rồi ghi đè 8 luật, nên một sửa đổi
ở phần nền (lịch, múi giờ, an Mệnh…) không bị quên ở đây.
"""

from __future__ import annotations

from cosmic_astrology.conventions.policies import (
    DaoHoaPolicy,
    HongLoanThienHyPolicy,
    KinhDuongDaLaPolicy,
    LocTonPolicy,
    RuleId,
    TaPhuHuuBatPolicy,
    ThienKhoiThienVietPolicy,
    ThienMaPolicy,
    VanXuongVanKhucPolicy,
    VerificationStatus,
)
from cosmic_astrology.conventions.profile import ConventionProfile, RuleBinding
from cosmic_astrology.conventions.provenance import SourceReference
from cosmic_astrology.conventions.standard import COSMIC_SIGNS_STANDARD_V1

__all__ = ["COSMIC_SIGNS_NAM_PHAI_V1", "NAM_PHAI_PROFILE_ID", "NAM_PHAI_PROFILE_VERSION"]

NAM_PHAI_PROFILE_ID = "COSMIC_SIGNS_NAM_PHAI_V1"
NAM_PHAI_PROFILE_VERSION = "2026.09"

V = VerificationStatus

#: Trường phái đã nêu tên, nhưng ấn bản thì chưa. Đây là hai việc khác nhau, và
#: gộp chúng lại là cách một cách đọc thông dụng bị đọc thành một trích dẫn.
_NAM_PHAI_COMMON_USAGE = SourceReference(
    note=(
        "Nam phái, theo cách đọc thông dụng. CHƯA chọn ấn bản cụ thể (Q2) và chưa "
        "có người thẩm định ký duyệt (Q3), nên đây không phải trích dẫn."
    )
)


def _nam_phai_rule(rule: RuleId, policy: str, note: str) -> RuleBinding:
    return RuleBinding(
        rule=rule,
        policy=policy,
        implemented=True,
        verification=V.PROVISIONAL,
        source=_NAM_PHAI_COMMON_USAGE,
        # Q1 (trường phái) đã trả lời là Nam phái; Q2/Q3 thì chưa.
        blocked_by=("Q2", "Q3"),
        note=note,
    )


_SUPPORTING_GROUP_1: dict[RuleId, RuleBinding] = {
    RuleId.VAN_XUONG_VAN_KHUC: _nam_phai_rule(
        RuleId.VAN_XUONG_VAN_KHUC,
        VanXuongVanKhucPolicy.HOUR_TUAT_REVERSE_THIN_FORWARD.value,
        "Xương khởi Tuất đếm nghịch theo giờ; Khúc khởi Thìn đếm thuận. Hệ quả "
        "kiểm được: hai sao đồng cung tại Mùi (giờ Mão) và Sửu (giờ Dậu).",
    ),
    RuleId.TA_PHU_HUU_BAT: _nam_phai_rule(
        RuleId.TA_PHU_HUU_BAT,
        TaPhuHuuBatPolicy.MONTH_THIN_FORWARD_TUAT_REVERSE.value,
        "Tả khởi Thìn đếm thuận, Hữu khởi Tuất đếm nghịch, tính từ tháng Giêng âm.",
    ),
    RuleId.THIEN_KHOI_THIEN_VIET: _nam_phai_rule(
        RuleId.THIEN_KHOI_THIEN_VIET,
        ThienKhoiThienVietPolicy.YEAR_STEM_TABLE_CANH_WITH_GIAP_MAU.value,
        "Bảng theo can năm ('Giáp Mậu Canh ngưu dương…'). Can Canh là chỗ các "
        "trường phái hay khác nhau; bản này xếp Canh cùng nhóm Giáp/Mậu.",
    ),
    RuleId.LOC_TON: _nam_phai_rule(
        RuleId.LOC_TON,
        LocTonPolicy.YEAR_STEM_LAM_QUAN.value,
        "Lộc Tồn tại cung lâm quan của can năm. Không bao giờ vào tứ mộ.",
    ),
    RuleId.KINH_DUONG_DA_LA: _nam_phai_rule(
        RuleId.KINH_DUONG_DA_LA,
        KinhDuongDaLaPolicy.ADJACENT_TO_LOC_TON.value,
        "'Tiền Kình hậu Đà': Kình ở cung liền sau Lộc Tồn theo chiều thuận, Đà ở "
        "cung liền trước. Hai sao luôn kẹp Lộc Tồn ở giữa.",
    ),
    RuleId.DAO_HOA: _nam_phai_rule(
        RuleId.DAO_HOA,
        DaoHoaPolicy.YEAR_BRANCH_TRINE.value,
        "Theo tam hợp chi năm. Luôn rơi vào tứ chính (Tý Ngọ Mão Dậu).",
    ),
    RuleId.HONG_LOAN_THIEN_HY: _nam_phai_rule(
        RuleId.HONG_LOAN_THIEN_HY,
        HongLoanThienHyPolicy.YEAR_BRANCH_MAO_REVERSE.value,
        "Hồng Loan khởi Mão năm Tý, đếm nghịch theo chi năm; Thiên Hỷ luôn đối cung.",
    ),
    RuleId.THIEN_MA: _nam_phai_rule(
        RuleId.THIEN_MA,
        ThienMaPolicy.YEAR_BRANCH_TRINE.value,
        "Dịch mã theo tam hợp chi năm. Luôn rơi vào tứ sinh (Dần Thân Tỵ Hợi).",
    ),
}

COSMIC_SIGNS_NAM_PHAI_V1 = ConventionProfile(
    profile_id=NAM_PHAI_PROFILE_ID,
    version=NAM_PHAI_PROFILE_VERSION,
    description=(
        "Nam phái. Kế thừa hồ sơ chuẩn và chọn thêm luật an nhóm phụ tinh 1. "
        "Toàn bộ ở mức PROVISIONAL: đã nêu trường phái nhưng chưa chốt ấn bản."
    ),
    rules={**COSMIC_SIGNS_STANDARD_V1.rules, **_SUPPORTING_GROUP_1},
)
