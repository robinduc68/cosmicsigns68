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
    AnQuangThienQuyPolicy,
    BacSiCyclePolicy,
    CoThanQuaTuPolicy,
    DaoHoaPolicy,
    DiaKhongDiaKiepPolicy,
    FourTransformationsPolicy,
    HoaCaiPolicy,
    HoaTinhLinhTinhPolicy,
    HongLoanThienHyPolicy,
    KiepSatPolicy,
    KinhDuongDaLaPolicy,
    LocTonPolicy,
    LongTriPhuongCacPolicy,
    QuocAnDuongPhuPolicy,
    RuleId,
    StarStrengthPolicy,
    TamThaiBatToaPolicy,
    TaPhuHuuBatPolicy,
    ThaiPhuPhongCaoPolicy,
    ThaiTueCyclePolicy,
    ThienDucNguyetDucPolicy,
    ThienGiaiDiaGiaiPolicy,
    ThienKhocThienHuPolicy,
    ThienKhoiThienVietPolicy,
    ThienKhongPolicy,
    ThienMaPolicy,
    ThienQuanThienPhucPolicy,
    ThienTaiThienThoPolicy,
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
    RuleId.LONG_TRI_PHUONG_CAC: _nam_phai_rule(
        RuleId.LONG_TRI_PHUONG_CAC,
        LongTriPhuongCacPolicy.YEAR_BRANCH_THIN_FORWARD_TUAT_REVERSE.value,
        "Long Trì khởi Thìn đếm thuận theo chi năm; Phượng Các khởi Tuất đếm nghịch. "
        "Hệ quả kiểm được: đồng cung tại Mùi (năm Mão) và Sửu (năm Dậu).",
    ),
    RuleId.TAM_THAI_BAT_TOA: _nam_phai_rule(
        RuleId.TAM_THAI_BAT_TOA,
        TamThaiBatToaPolicy.FROM_TA_PHU_HUU_BAT_BY_LUNAR_DAY.value,
        "Tam Thai từ Tả Phù đếm thuận tới ngày âm; Bát Tọa từ Hữu Bật đếm nghịch. "
        "Phụ thuộc vị trí Tả Phù / Hữu Bật, nên phải an sau nhóm 1.",
    ),
    RuleId.AN_QUANG_THIEN_QUY: _nam_phai_rule(
        RuleId.AN_QUANG_THIEN_QUY,
        AnQuangThienQuyPolicy.FROM_XUONG_KHUC_BY_LUNAR_DAY_BACK_ONE.value,
        "Ân Quang từ Văn Xương, Thiên Quý từ Văn Khúc: đếm thuận tới ngày âm rồi lùi "
        "một cung. Bước 'lùi một cung' là chỗ các bản ghi khác nhau.",
    ),
    RuleId.THIEN_DUC_NGUYET_DUC: _nam_phai_rule(
        RuleId.THIEN_DUC_NGUYET_DUC,
        ThienDucNguyetDucPolicy.YEAR_BRANCH_DAU_AND_TY.value,
        "Thiên Đức khởi Dậu, Nguyệt Đức khởi Tỵ, cùng đếm thuận theo chi năm. Hai sao "
        "luôn cách nhau 4 cung. Một số bản an theo tháng âm thay vì chi năm.",
    ),
    RuleId.THAI_TUE_CYCLE: _nam_phai_rule(
        RuleId.THAI_TUE_CYCLE,
        ThaiTueCyclePolicy.YEAR_BRANCH_FORWARD.value,
        "Vòng Thái Tuế khởi tại chi năm, đi thuận. Nhóm này CHỈ an Thiếu Dương, "
        "Thiếu Âm, Long Đức, Phúc Đức; các sao còn lại thuộc nhóm sau.",
    ),
    RuleId.HOA_CAI: _nam_phai_rule(
        RuleId.HOA_CAI,
        HoaCaiPolicy.YEAR_BRANCH_TRINE_TOMB.value,
        "Hoa Cái tại cung mộ của tam hợp chi năm. Luôn rơi vào tứ mộ.",
    ),
    RuleId.THIEN_TAI_THIEN_THO: _nam_phai_rule(
        RuleId.THIEN_TAI_THIEN_THO,
        ThienTaiThienThoPolicy.FROM_MENH_AND_THAN_BY_YEAR_BRANCH.value,
        "Thiên Tài từ cung Mệnh, Thiên Thọ từ cung Thân, cùng đếm thuận theo chi năm.",
    ),
    RuleId.THIEN_QUAN_THIEN_PHUC: _nam_phai_rule(
        RuleId.THIEN_QUAN_THIEN_PHUC,
        ThienQuanThienPhucPolicy.YEAR_STEM_TABLE.value,
        "Thiên Quan và Thiên Phúc Quý Nhân, mỗi sao một bảng theo can năm sinh.",
    ),
    RuleId.THIEN_GIAI_DIA_GIAI: _nam_phai_rule(
        RuleId.THIEN_GIAI_DIA_GIAI,
        ThienGiaiDiaGiaiPolicy.LUNAR_MONTH_THAN_AND_MUI.value,
        "Thiên Giải khởi Thân, Địa Giải khởi Mùi, cùng đếm thuận theo tháng âm. "
        "Hệ quả: hai sao luôn đứng liền kề.",
    ),
    RuleId.THAI_PHU_PHONG_CAO: _nam_phai_rule(
        RuleId.THAI_PHU_PHONG_CAO,
        ThaiPhuPhongCaoPolicy.HOUR_NGO_AND_DAN_FORWARD.value,
        "Thai Phụ khởi Ngọ, Phong Cáo khởi Dần, cùng đếm thuận theo giờ sinh. Cách "
        "phát biểu 'Văn Khúc ± 2 cung' cho cùng kết quả ở cả 12 giờ — một luật, hai "
        "cách nói, không phải hai luật mâu thuẫn.",
    ),
    RuleId.QUOC_AN_DUONG_PHU: _nam_phai_rule(
        RuleId.QUOC_AN_DUONG_PHU,
        QuocAnDuongPhuPolicy.OFFSET_FROM_LOC_TON.value,
        "Quốc Ấn cách Lộc Tồn 8 cung, Đường Phù cách 5 cung, đều theo chiều thuận. "
        "Bảng theo can năm khớp đúng hai offset này ở cả 10 can.",
    ),
    RuleId.BAC_SI_CYCLE: _nam_phai_rule(
        RuleId.BAC_SI_CYCLE,
        BacSiCyclePolicy.FROM_LOC_TON_YANG_MALE_FORWARD.value,
        "Vòng Bác Sĩ khởi tại Lộc Tồn; dương nam / âm nữ đi thuận, cùng luật chiều "
        "với đại vận. Nhóm này CHỈ an Hỷ Thần; các sao còn lại thuộc nhóm sau.",
    ),
    RuleId.DIA_KHONG_DIA_KIEP: _nam_phai_rule(
        RuleId.DIA_KHONG_DIA_KIEP,
        DiaKhongDiaKiepPolicy.HOUR_FROM_HOI_BOTH_DIRECTIONS.value,
        "Cùng khởi Hợi giờ Tý: Địa Kiếp đếm thuận, Địa Không đếm nghịch theo giờ "
        "sinh. Hệ quả: đồng cung tại Hợi (giờ Tý) và Tỵ (giờ Ngọ).",
    ),
    RuleId.HOA_TINH_LINH_TINH: _nam_phai_rule(
        RuleId.HOA_TINH_LINH_TINH,
        HoaTinhLinhTinhPolicy.TRINE_START_YANG_MALE_FORWARD.value,
        "Địa chi khởi theo tam hợp chi năm, rồi đếm theo giờ sinh. CHIỀU là chỗ các "
        "bản khác nhau: bản này lấy dương nam / âm nữ đi thuận; một số bản cho cả "
        "hai sao luôn đi thuận.",
    ),
    RuleId.KIEP_SAT: _nam_phai_rule(
        RuleId.KIEP_SAT,
        KiepSatPolicy.YEAR_BRANCH_TRINE.value,
        "Kiếp Sát tại cung tuyệt của tam hợp chi năm. Luôn rơi vào tứ sinh.",
    ),
    RuleId.CO_THAN_QUA_TU: _nam_phai_rule(
        RuleId.CO_THAN_QUA_TU,
        CoThanQuaTuPolicy.YEAR_BRANCH_SEASON.value,
        "Cô Thần và Quả Tú theo mùa của chi năm. Cô Thần luôn ở tứ sinh, Quả Tú "
        "luôn ở tứ mộ, hai sao luôn cách nhau 4 cung.",
    ),
    RuleId.THIEN_KHONG: _nam_phai_rule(
        RuleId.THIEN_KHONG,
        ThienKhongPolicy.ONE_AFTER_THAI_TUE.value,
        "Thiên Không ở cung liền sau Thái Tuế, nên luôn đồng cung Thiếu Dương. "
        "KHÁC HOÀN TOÀN Địa Không — khác luật, khác mã sao.",
    ),
    RuleId.THIEN_KHOC_THIEN_HU: _nam_phai_rule(
        RuleId.THIEN_KHOC_THIEN_HU,
        ThienKhocThienHuPolicy.YEAR_BRANCH_FROM_NGO_SYMMETRIC.value,
        "Cùng khởi Ngọ năm Tý: Khốc đếm nghịch, Hư đếm thuận theo chi năm. Đồng "
        "cung tại Ngọ (năm Tý) và Tý (năm Ngọ).",
    ),
    RuleId.FOUR_TRANSFORMATIONS: RuleBinding(
        rule=RuleId.FOUR_TRANSFORMATIONS,
        policy=FourTransformationsPolicy.NAM_PHAI_TABLE_V1.value,
        implemented=True,
        verification=V.PROVISIONAL,
        source=_NAM_PHAI_COMMON_USAGE,
        # Q7 (hàng Canh) vẫn mở: bảng đã CHỌN một phương án chứ chưa GIẢI được câu hỏi.
        blocked_by=("Q2", "Q3", "Q7"),
        note=(
            "Bảng theo can năm. Hàng Canh chọn phương án 'Thái Âm Khoa, Thiên Đồng Kỵ' "
            "(đa số bản Việt); hai biến thể còn lại đổi chỗ Khoa/Kỵ và nằm sẵn trong "
            "stars/four_transformations.py. Hàng Mậu chọn Hữu Bật Khoa, hàng Nhâm chọn "
            "Tả Phù Khoa — cả hai đều có cách đọc đối lập."
        ),
    ),
    RuleId.STAR_STRENGTH: RuleBinding(
        rule=RuleId.STAR_STRENGTH,
        policy=StarStrengthPolicy.NAM_PHAI_TABLE_V1.value,
        # Cơ chế đã cài và chạy; BẢNG thì chưa có. Hai việc khác nhau, và đánh dấu
        # implemented=True lúc này sẽ là nói dối về thứ khách nhận được.
        implemented=False,
        verification=V.UNVERIFIED,
        source=_NAM_PHAI_COMMON_USAGE,
        blocked_by=("Q2", "Q3"),
        note=(
            "Tra cứu star_id + địa chi đã nối xong, nhưng bảng 168 ô còn RỖNG nên mọi "
            "độ sáng là null. Bảng phải do người thẩm định chép từ ấn bản đã chốt vào "
            "stars/data/nam_phai_star_strength_v1.json — không suy ra được bằng công thức. "
            "Điền xong đổi implemented=True; điền đủ KHÔNG tự thành VERIFIED."
        ),
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
