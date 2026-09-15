"""Every school-dependent choice the engine makes, named and enumerated.

The point of this module is negative: after it exists, a Tử Vi rule that varies
between schools may **not** live as an unnamed branch inside calculation code.
It has to be a policy value here, selected by a convention profile, so that two
charts built under different assumptions can never be mistaken for each other.

Policies whose value is ``UNRESOLVED`` are open questions (see
``docs/astrology-conventions.md``). They are not defaults and not placeholders
to be quietly filled in: asking the engine to apply one is an error.
"""

from __future__ import annotations

from enum import StrEnum

__all__ = [
    "BirthTimeCorrectionPolicy",
    "CalendarPolicy",
    "CucPolicy",
    "DayBoundaryPolicy",
    "FourTransformationsPolicy",
    "LateZiPolicy",
    "MajorCycleDirectionPolicy",
    "MajorCycleStartAgePolicy",
    "MajorStarPolicy",
    "MenhPolicy",
    "PalaceOrderPolicy",
    "PalaceStemPolicy",
    "RuleId",
    "StarStrengthPolicy",
    "ThanPolicy",
    "TimezonePolicy",
    "TrietPolicy",
    "TuViPolicy",
    "TuanPolicy",
    "VerificationStatus",
    "YinYangPolicy",
]

UNRESOLVED = "UNRESOLVED"


class RuleId(StrEnum):
    """Stable identifiers for the rules a profile has to pin down."""

    CALENDAR = "calendar"
    TIMEZONE = "timezone"
    BIRTH_TIME_CORRECTION = "birth_time_correction"
    DAY_BOUNDARY = "day_boundary"
    LATE_ZI = "late_zi"
    YIN_YANG = "yin_yang"
    MENH_PLACEMENT = "menh_placement"
    THAN_PLACEMENT = "than_placement"
    CUC = "cuc"
    PALACE_ORDER = "palace_order"
    PALACE_STEMS = "palace_stems"
    TU_VI_PLACEMENT = "tu_vi_placement"
    MAJOR_STARS = "major_stars"
    VAN_XUONG_VAN_KHUC = "van_xuong_van_khuc"
    TA_PHU_HUU_BAT = "ta_phu_huu_bat"
    THIEN_KHOI_THIEN_VIET = "thien_khoi_thien_viet"
    LOC_TON = "loc_ton"
    KINH_DUONG_DA_LA = "kinh_duong_da_la"
    DAO_HOA = "dao_hoa"
    HONG_LOAN_THIEN_HY = "hong_loan_thien_hy"
    THIEN_MA = "thien_ma"
    LONG_TRI_PHUONG_CAC = "long_tri_phuong_cac"
    TAM_THAI_BAT_TOA = "tam_thai_bat_toa"
    AN_QUANG_THIEN_QUY = "an_quang_thien_quy"
    THIEN_DUC_NGUYET_DUC = "thien_duc_nguyet_duc"
    THAI_TUE_CYCLE = "thai_tue_cycle"
    HOA_CAI = "hoa_cai"
    THIEN_TAI_THIEN_THO = "thien_tai_thien_tho"
    THIEN_QUAN_THIEN_PHUC = "thien_quan_thien_phuc"
    THIEN_GIAI_DIA_GIAI = "thien_giai_dia_giai"
    THAI_PHU_PHONG_CAO = "thai_phu_phong_cao"
    QUOC_AN_DUONG_PHU = "quoc_an_duong_phu"
    BAC_SI_CYCLE = "bac_si_cycle"
    DIA_KHONG_DIA_KIEP = "dia_khong_dia_kiep"
    HOA_TINH_LINH_TINH = "hoa_tinh_linh_tinh"
    KIEP_SAT = "kiep_sat"
    CO_THAN_QUA_TU = "co_than_qua_tu"
    THIEN_KHONG = "thien_khong"
    THIEN_KHOC_THIEN_HU = "thien_khoc_thien_hu"
    PHA_TOAI = "pha_toai"
    THIEN_HINH_THIEN_DIEU = "thien_hinh_thien_dieu"
    THIEN_LA_DIA_VONG = "thien_la_dia_vong"
    THIEN_THUONG_THIEN_SU = "thien_thuong_thien_su"
    DAU_QUAN = "dau_quan"
    LUU_VAN_XUONG_VAN_KHUC = "luu_van_xuong_van_khuc"
    STAR_ELEMENTS = "star_elements"
    FOUR_TRANSFORMATIONS = "four_transformations"
    TUAN = "tuan"
    TRIET = "triet"
    STAR_STRENGTH = "star_strength"
    TRANG_SINH_START = "trang_sinh_start"
    TRANG_SINH_DIRECTION = "trang_sinh_direction"
    MAJOR_CYCLE_DIRECTION = "major_cycle_direction"
    MAJOR_CYCLE_START_AGE = "major_cycle_start_age"
    CHU_MENH_CHU_THAN = "chu_menh_chu_than"
    LUU_HA = "luu_ha"
    THIEN_TRU = "thien_tru"
    THIEN_Y = "thien_y"
    GIAI_THAN = "giai_than"


class VerificationStatus(StrEnum):
    """How much trust a rule has earned.

    Deliberately separate from "is it implemented". A rule can be fully coded and
    still be ``PROVISIONAL`` — that is exactly the state the 14 major stars are
    in today, and conflating the two is how an unverified chart ends up being
    presented as authoritative.
    """

    UNVERIFIED = "UNVERIFIED"
    PROVISIONAL = "PROVISIONAL"
    VERIFIED = "VERIFIED"


class CalendarPolicy(StrEnum):
    MEEUS_CH49_VIETNAM = "MEEUS_CH49_VIETNAM"


class TimezonePolicy(StrEnum):
    """Where the UTC offset of the birth moment comes from."""

    #: Resolve from the IANA database at the birth instant. Correct across the
    #: historical offset changes Vietnam went through.
    IANA_HISTORICAL = "IANA_HISTORICAL"
    #: Caller supplies a fixed offset. Kept for explicit, deliberate overrides.
    FIXED_OFFSET = "FIXED_OFFSET"


class BirthTimeCorrectionPolicy(StrEnum):
    """Whether clock time is corrected towards local solar time.

    Distinct from :class:`TimezonePolicy` on purpose: a timezone answers "what
    did the clock on the wall read", a correction answers "where was the sun".
    Conflating them is a common way to be wrong twice.
    """

    NONE = "NONE"
    #: Not implemented — the convention has to define the exact correction first.
    TRUE_SOLAR_TIME = "TRUE_SOLAR_TIME"


class DayBoundaryPolicy(StrEnum):
    LOCAL_MIDNIGHT = "LOCAL_MIDNIGHT"


class LateZiPolicy(StrEnum):
    """What a birth at 23:00–23:59 belongs to. **Open question Q6.**

    Giờ Tý straddles midnight, so a birth in its first half can be argued to
    belong to either civil day. The three positions below are all held by real
    schools; the engine refuses to guess between them.
    """

    #: No policy chosen. Asking the engine to place a late-Zi birth raises.
    UNRESOLVED = UNRESOLVED
    #: 23:xx stays on the current civil day for everything.
    CIVIL_DAY = "CIVIL_DAY"
    #: 23:xx belongs to the next day for everything — lunar day and day pillar.
    LATE_ZI_NEXT_DAY = "LATE_ZI_NEXT_DAY"
    #: Day pillar advances, the lunar day used for star placement does not.
    #: Asymmetric by design, not by accident — see docs before selecting it.
    PILLAR_ONLY_NEXT_DAY = "PILLAR_ONLY_NEXT_DAY"


class YinYangPolicy(StrEnum):
    YEAR_STEM_PARITY = "YEAR_STEM_PARITY"


class MenhPolicy(StrEnum):
    #: From Dần, forward to the lunar month, then backward by the hour branch.
    DAN_FORWARD_MONTH_BACKWARD_HOUR = "DAN_FORWARD_MONTH_BACKWARD_HOUR"


class ThanPolicy(StrEnum):
    #: From Dần, forward to the lunar month, then forward by the hour branch.
    DAN_FORWARD_MONTH_FORWARD_HOUR = "DAN_FORWARD_MONTH_FORWARD_HOUR"


class CucPolicy(StrEnum):
    #: Cục from the nạp âm of the Mệnh palace's stem+branch.
    NAP_AM_OF_MENH_PALACE = "NAP_AM_OF_MENH_PALACE"


class PalaceOrderPolicy(StrEnum):
    """How the twelve palace names are laid onto the địa chi.

    The value name is kept as stored in existing charts. It describes the classical
    sequence Mệnh → Huynh Đệ → Phu Thê → Tử Tức → Tài Bạch → Tật Ách → Thiên Di →
    Nô Bộc → Quan Lộc → Điền Trạch → Phúc Đức → Phụ Mẫu walking counter-clockwise,
    which puts Phụ Mẫu one step *clockwise* of Mệnh.
    """

    COUNTER_CLOCKWISE_FROM_MENH = "COUNTER_CLOCKWISE_FROM_MENH"


class PalaceStemPolicy(StrEnum):
    NGU_HO_DON = "NGU_HO_DON"


class TuViPolicy(StrEnum):
    #: Classical cục-remainder walk from Dần.
    CUC_REMAINDER_CLASSICAL = "CUC_REMAINDER_CLASSICAL"


class MajorStarPolicy(StrEnum):
    #: Tử Vi chain counter-clockwise, Thiên Phủ chain clockwise about Dần–Thân.
    TWO_CHAINS_CLASSICAL = "TWO_CHAINS_CLASSICAL"


class LongTriPhuongCacPolicy(StrEnum):
    """Long Trì / Phượng Các theo chi năm.

    Hệ quả kiểm được: hai sao đồng cung tại Mùi (năm Mão) và Sửu (năm Dậu).
    """

    YEAR_BRANCH_THIN_FORWARD_TUAT_REVERSE = "YEAR_BRANCH_THIN_FORWARD_TUAT_REVERSE"


class TamThaiBatToaPolicy(StrEnum):
    """Tam Thai / Bát Tọa theo Tả Phù, Hữu Bật và ngày âm."""

    FROM_TA_PHU_HUU_BAT_BY_LUNAR_DAY = "FROM_TA_PHU_HUU_BAT_BY_LUNAR_DAY"


class AnQuangThienQuyPolicy(StrEnum):
    """Ân Quang / Thiên Quý theo Văn Xương, Văn Khúc và ngày âm.

    Hai cách an, khác nhau ở **chiều đếm của Thiên Quý** — không phải ở bước
    "lùi một cung" như ghi chú cũ của dự án từng đoán.
    """

    #: Cả hai sao đếm **thuận** rồi lùi một cung. Đây là cách dự án cài lúc đầu:
    #: một phép đối xứng hoá do người viết tự suy ra, không có bản đối chiếu nào
    #: chống lưng. Giữ lại để còn gọi tên được thứ đã bị thay.
    FROM_XUONG_KHUC_BY_LUNAR_DAY_BACK_ONE = "FROM_XUONG_KHUC_BY_LUNAR_DAY_BACK_ONE"

    #: Hai sao **soi gương nhau**: Ân Quang từ Văn Xương đếm thuận rồi lùi một cung;
    #: Thiên Quý từ Văn Khúc đếm **nghịch** rồi lùi một cung — "lùi" ở đây là lùi
    #: ngược chiều đếm, tức tiến một bậc theo thứ tự địa chi.
    XUONG_FORWARD_KHUC_BACKWARD_MIRRORED = "XUONG_FORWARD_KHUC_BACKWARD_MIRRORED"


class ThienDucNguyetDucPolicy(StrEnum):
    """Thiên Đức / Nguyệt Đức theo chi năm."""

    YEAR_BRANCH_DAU_AND_TY = "YEAR_BRANCH_DAU_AND_TY"


class ThaiTueCyclePolicy(StrEnum):
    """Vòng Thái Tuế, khởi tại chi năm và đi thuận.

    Nhóm này **chỉ an bốn sao** trong vòng: Thiếu Dương, Thiếu Âm, Long Đức,
    Phúc Đức. Các sao còn lại thuộc nhóm sau.
    """

    YEAR_BRANCH_FORWARD = "YEAR_BRANCH_FORWARD"


class HoaCaiPolicy(StrEnum):
    """Hoa Cái theo tam hợp chi năm. Luôn rơi vào tứ mộ."""

    YEAR_BRANCH_TRINE_TOMB = "YEAR_BRANCH_TRINE_TOMB"


class ThienTaiThienThoPolicy(StrEnum):
    """Thiên Tài / Thiên Thọ tính từ cung Mệnh và cung Thân theo chi năm."""

    FROM_MENH_AND_THAN_BY_YEAR_BRANCH = "FROM_MENH_AND_THAN_BY_YEAR_BRANCH"


class ThienQuanThienPhucPolicy(StrEnum):
    """Thiên Quan / Thiên Phúc Quý Nhân theo thiên can năm sinh."""

    YEAR_STEM_TABLE = "YEAR_STEM_TABLE"


class ThienGiaiDiaGiaiPolicy(StrEnum):
    """Thiên Giải / Địa Giải theo tháng âm. Hai sao luôn đứng liền kề."""

    LUNAR_MONTH_THAN_AND_MUI = "LUNAR_MONTH_THAN_AND_MUI"


class ThaiPhuPhongCaoPolicy(StrEnum):
    """Thai Phụ / Phong Cáo theo giờ sinh.

    Phát biểu "Văn Khúc ± 2 cung" cho **cùng một kết quả** ở cả 12 giờ, nên đây là
    một luật chứ không phải hai.
    """

    HOUR_NGO_AND_DAN_FORWARD = "HOUR_NGO_AND_DAN_FORWARD"


class QuocAnDuongPhuPolicy(StrEnum):
    """Quốc Ấn / Đường Phù, cách Lộc Tồn 8 và 5 cung.

    Bảng theo can năm mà các sách ghi ra đúng bằng hai offset cố định này ở cả 10
    can — hai cách phát biểu độc lập trùng khớp.
    """

    OFFSET_FROM_LOC_TON = "OFFSET_FROM_LOC_TON"


class BacSiCyclePolicy(StrEnum):
    """Vòng Bác Sĩ, khởi tại Lộc Tồn, chiều theo âm dương nam nữ.

    Nhóm này **chỉ an Hỷ Thần**; Đại Hao, Tiểu Hao… thuộc nhóm sau.
    """

    FROM_LOC_TON_YANG_MALE_FORWARD = "FROM_LOC_TON_YANG_MALE_FORWARD"


class DiaKhongDiaKiepPolicy(StrEnum):
    """Địa Không / Địa Kiếp theo giờ sinh, cùng khởi từ Hợi.

    Hệ quả kiểm được: đồng cung tại Hợi (giờ Tý) và Tỵ (giờ Ngọ).
    """

    HOUR_FROM_HOI_BOTH_DIRECTIONS = "HOUR_FROM_HOI_BOTH_DIRECTIONS"


class HoaTinhLinhTinhPolicy(StrEnum):
    """Hỏa Tinh / Linh Tinh: địa chi khởi theo tam hợp chi năm, đếm theo giờ sinh.

    **Chiều là chỗ các bản khác nhau.** Bản này lấy dương nam / âm nữ đi thuận,
    cùng luật chiều với đại vận; một số bản cho cả hai sao luôn đi thuận.
    """

    TRINE_START_YANG_MALE_FORWARD = "TRINE_START_YANG_MALE_FORWARD"


class KiepSatPolicy(StrEnum):
    """Kiếp Sát tại cung tuyệt của tam hợp chi năm. Luôn rơi vào tứ sinh."""

    YEAR_BRANCH_TRINE = "YEAR_BRANCH_TRINE"


class CoThanQuaTuPolicy(StrEnum):
    """Cô Thần / Quả Tú theo mùa của chi năm. Luôn cách nhau 4 cung."""

    YEAR_BRANCH_SEASON = "YEAR_BRANCH_SEASON"


class ThienKhongPolicy(StrEnum):
    """Thiên Không: cung liền sau Thái Tuế.

    Hệ quả là **luôn đồng cung Thiếu Dương** — kết quả đúng, không phải trùng lặp.
    Đây không phải Địa Không.
    """

    ONE_AFTER_THAI_TUE = "ONE_AFTER_THAI_TUE"


class ThienKhocThienHuPolicy(StrEnum):
    """Thiên Khốc / Thiên Hư: cặp đối xứng qua trục Tý–Ngọ, khởi Ngọ năm Tý."""

    YEAR_BRANCH_FROM_NGO_SYMMETRIC = "YEAR_BRANCH_FROM_NGO_SYMMETRIC"


class PhaToaiPolicy(StrEnum):
    """Phá Toái theo nhóm chi năm: tứ chính → Tỵ, tứ sinh → Sửu, tứ mộ → Dậu."""

    YEAR_BRANCH_GROUP = "YEAR_BRANCH_GROUP"


class ThienHinhThienDieuPolicy(StrEnum):
    """Thiên Hình / Thiên Diêu theo tháng âm. Luôn cách nhau 8 cung."""

    LUNAR_MONTH_DAU_AND_SUU = "LUNAR_MONTH_DAU_AND_SUU"


class ThienLaDiaVongPolicy(StrEnum):
    """Thiên La tại Thìn, Địa Võng tại Tuất — **cố định**, không phụ thuộc ngày sinh."""

    FIXED_THIN_AND_TUAT = "FIXED_THIN_AND_TUAT"


class ThienThuongThienSuPolicy(StrEnum):
    """Thiên Thương tại cung Nô Bộc, Thiên Sứ tại cung Tật Ách.

    Gắn vào **cung**, nhưng engine vẫn trả về địa chi — cung nào ở địa chi nào là
    việc engine đã biết, và frontend không được tự suy.
    """

    NO_BOC_AND_TAT_ACH = "NO_BOC_AND_TAT_ACH"


class DauQuanPolicy(StrEnum):
    """Đẩu Quân: từ Thái Tuế đếm nghịch tới tháng sinh, rồi thuận tới giờ sinh."""

    THAI_TUE_MONTH_REVERSE_HOUR_FORWARD = "THAI_TUE_MONTH_REVERSE_HOUR_FORWARD"


class LuuVanXuongVanKhucPolicy(StrEnum):
    """Lưu Văn Xương / Lưu Văn Khúc theo **thiên can năm xem**.

    Khác hẳn Văn Xương / Văn Khúc bản mệnh, vốn an theo **giờ sinh** — đây là hai
    họ luật khác nhau, không phải cùng một luật đổi đầu vào.
    """

    YEAR_STEM_FROM_LOC_TON = "YEAR_STEM_FROM_LOC_TON"


class FourTransformationsPolicy(StrEnum):
    """Bảng Tứ Hóa theo thiên can năm sinh.

    **Q7 vẫn mở.** Hàng Canh có ba biến thể được ghi nhận, và hai trong số đó đổi
    chỗ Hóa Khoa với Hóa Kỵ — tức lật một cát tinh thành hung tinh trên mọi lá số
    sinh năm Canh. Bảng Nam phái dưới đây chọn phương án đa số bản Việt và ghi cả
    ba biến thể trong ``stars/four_transformations.py``.
    """

    NAM_PHAI_TABLE_V1 = "NAM_PHAI_TABLE_V1"
    UNRESOLVED = UNRESOLVED


class TuanPolicy(StrEnum):
    YEAR_PILLAR_DECADE = "YEAR_PILLAR_DECADE"


class TrietPolicy(StrEnum):
    #: Table by year stem, both branches weighted equally. **Q10** asks whether
    #: the two branches should carry different weight.
    YEAR_STEM_TABLE_EQUAL_WEIGHT = "YEAR_STEM_TABLE_EQUAL_WEIGHT"


class VanXuongVanKhucPolicy(StrEnum):
    """Văn Xương / Văn Khúc theo giờ sinh."""

    #: Xương khởi Tuất đếm nghịch, Khúc khởi Thìn đếm thuận. Hệ quả kiểm được:
    #: hai sao đồng cung tại Sửu (giờ Dậu) và Mùi (giờ Mão).
    HOUR_TUAT_REVERSE_THIN_FORWARD = "HOUR_TUAT_REVERSE_THIN_FORWARD"


class TaPhuHuuBatPolicy(StrEnum):
    """Tả Phù / Hữu Bật theo tháng âm."""

    #: Tả khởi Thìn đếm thuận, Hữu khởi Tuất đếm nghịch, từ tháng Giêng.
    MONTH_THIN_FORWARD_TUAT_REVERSE = "MONTH_THIN_FORWARD_TUAT_REVERSE"


class ThienKhoiThienVietPolicy(StrEnum):
    """Thiên Khôi / Thiên Việt theo thiên can năm sinh."""

    #: Bảng theo câu quyết "Giáp Mậu Canh ngưu dương…". Chỗ các trường phái hay
    #: khác nhau là can **Canh**; bản này xếp Canh cùng nhóm Giáp/Mậu.
    YEAR_STEM_TABLE_CANH_WITH_GIAP_MAU = "YEAR_STEM_TABLE_CANH_WITH_GIAP_MAU"


class LocTonPolicy(StrEnum):
    """Lộc Tồn theo thiên can năm sinh — cung lâm quan của can."""

    YEAR_STEM_LAM_QUAN = "YEAR_STEM_LAM_QUAN"


class KinhDuongDaLaPolicy(StrEnum):
    """Kình Dương / Đà La kẹp hai bên Lộc Tồn."""

    #: "Tiền Kình hậu Đà": Kình ở cung liền sau, Đà ở cung liền trước.
    ADJACENT_TO_LOC_TON = "ADJACENT_TO_LOC_TON"


class DaoHoaPolicy(StrEnum):
    """Đào Hoa theo tam hợp chi năm. Luôn rơi vào tứ chính."""

    YEAR_BRANCH_TRINE = "YEAR_BRANCH_TRINE"


class HongLoanThienHyPolicy(StrEnum):
    """Hồng Loan / Thiên Hỷ theo chi năm."""

    #: Hồng Loan khởi Mão năm Tý đếm nghịch; Thiên Hỷ luôn đối cung.
    YEAR_BRANCH_MAO_REVERSE = "YEAR_BRANCH_MAO_REVERSE"


class ThienMaPolicy(StrEnum):
    """Thiên Mã (dịch mã) theo tam hợp chi năm. Luôn rơi vào tứ sinh."""

    YEAR_BRANCH_TRINE = "YEAR_BRANCH_TRINE"


class StarElementPolicy(StrEnum):
    """Where a star's own ngũ hành comes from.

    Separate from ``STAR_STRENGTH``: strength is a 14 × 12 table that depends on
    the palace, while a star's element is a property of the star alone. Recorded
    only where the classical readings agree — the rest stay empty on purpose, so
    this policy is *partial* by name and cannot be mistaken for complete.
    """

    CLASSICAL_CONSENSUS_PARTIAL = "CLASSICAL_CONSENSUS_PARTIAL"


class StarStrengthPolicy(StrEnum):
    """Bảng miếu/vượng/đắc/bình/hãm.

    168 ô, **không suy ra được bằng công thức** — phải chép từ một ấn bản cụ thể.
    Policy chỉ nói *dùng bảng nào*; nội dung bảng nằm ở file dữ liệu riêng để người
    thẩm định điền mà không phải đụng code. Bảng Nam phái hiện **rỗng**.
    """

    NAM_PHAI_TABLE_V1 = "NAM_PHAI_TABLE_V1"
    UNRESOLVED = UNRESOLVED


class TrangSinhStartPolicy(StrEnum):
    """Which branch vòng Tràng Sinh begins on, given the ngũ hành of the Cục.

    Kim → Tỵ, Mộc → Hợi, Thủy → Thân, Hỏa → Dần are read the same way everywhere.
    **Thổ is not**, and the two readings move the whole cycle by six branches for
    every Thổ Ngũ Cục chart, so the choice cannot be left implicit.
    """

    #: Thổ starts where Thủy does (Thân). The majority reading in Vietnamese texts.
    CUC_ELEMENT_THO_WITH_THUY = "CUC_ELEMENT_THO_WITH_THUY"
    #: Thổ starts where Hỏa does (Dần).
    CUC_ELEMENT_THO_WITH_HOA = "CUC_ELEMENT_THO_WITH_HOA"


class TrangSinhDirectionPolicy(StrEnum):
    """Which way vòng Tràng Sinh runs around the địa bàn.

    The two readings disagree on half of all charts, so this is not a detail.
    """

    #: Dương nam and âm nữ thuận; âm nam and dương nữ nghịch — the same rule as
    #: đại vận. The majority reading.
    YANG_MALE_YIN_FEMALE_FORWARD = "YANG_MALE_YIN_FEMALE_FORWARD"
    #: Direction taken from the âm dương of the Cục instead of the subject.
    CUC_POLARITY = "CUC_POLARITY"


class MajorCycleDirectionPolicy(StrEnum):
    YANG_MALE_YIN_FEMALE_FORWARD = "YANG_MALE_YIN_FEMALE_FORWARD"


class MajorCycleStartAgePolicy(StrEnum):
    """Which age the first đại vận starts at.

    The sources agree it is the Cục number. What they do not settle is **what an
    age counts** — tuổi ta or completed years — which is open question **Q11**.
    That distinction does not change any number below; it changes how an age maps
    to a calendar year, which is why lưu niên stays blocked.
    """

    CUC_NUMBER = "CUC_NUMBER"
    UNRESOLVED = UNRESOLVED


class ChuMenhChuThanPolicy(StrEnum):
    """Chủ Mệnh / Chủ Thân — hai bảng tra theo **chi năm sinh**.

    Không phải sao an vào cung: đây là hai *nhãn* ghi ở khối giữa lá số, nói sao nào
    cai quản Mệnh và sao nào cai quản Thân. Vì thế chúng nằm ở ``traditional`` chứ
    không nằm trong danh sách sao — thêm chúng vào ``stars`` sẽ làm mọi phép đếm sai.
    """

    #: Hai bảng **đối xứng gương qua trục Tý–Ngọ**. Tính đối xứng ấy không phải trang
    #: trí: nó là chốt kiểm — một ô gõ sai sẽ phá đối xứng và test bắt được ngay.
    YEAR_BRANCH_TABLE_MIRRORED = "YEAR_BRANCH_TABLE_MIRRORED"


class LuuHaPolicy(StrEnum):
    """Lưu Hà — bảng tra theo **can năm**, 10 ô.

    Bảng này từng bị dự án xếp vào diện *chưa cài được* vì hai ô cuối (Nhâm, Quý)
    phá mất quy luật giảm dần của tám ô đầu, và người viết cho rằng mình nhớ sai.
    Chỗ bất quy tắc ấy **có thật trong bảng** — nó là đặc điểm của bảng, không phải
    dấu hiệu chép sai.
    """

    YEAR_STEM_TABLE = "YEAR_STEM_TABLE"


class ThienTruPolicy(StrEnum):
    """Thiên Trù — bảng tra theo **can năm**, 10 ô.

    **Nguồn của bảng chưa xác định.** Một hàng (Kỷ) đọc được từ lá số đối chiếu; chín
    hàng còn lại nêu lại từ trí nhớ, và trí nhớ ấy đã bị bắt sai đúng ở hàng có bằng
    chứng. Xem ``THIEN_TRU_UNVERIFIED_STEMS``.
    """

    #: Bảng ghép: một hàng có bằng chứng, chín hàng chưa. Tên policy nói thẳng điều đó
    #: để không ai đọc nhầm nó thành "đã chép từ một ấn bản".
    YEAR_STEM_TABLE_SOURCE_UNRESOLVED = "YEAR_STEM_TABLE_SOURCE_UNRESOLVED"


class ThienYPolicy(StrEnum):
    """Thiên Y — theo tháng âm."""

    #: Khởi Sửu tháng Giêng, đếm thuận. Hệ quả: **luôn đồng cung Thiên Diêu**.
    START_SUU_FORWARD_BY_MONTH = "START_SUU_FORWARD_BY_MONTH"


class GiaiThanPolicy(StrEnum):
    """Giải Thần — hai luật ứng viên. Bản đối chiếu đã **bác bỏ** một trong hai.

    Giữ cả hai ở đây để lựa chọn nằm lộ thiên. Đổi ``SELECTED_GIAI_THAN_VARIANT`` là
    đổi được cả engine, không phải đi sửa công thức rải rác.
    """

    #: Theo cặp tháng âm: 1–2 Thân, rồi mỗi hai tháng tiến hai cung. **Đã bị bác bỏ**
    #: bởi lá số đối chiếu: nó cho Thìn, bản đối chiếu ghi Mùi.
    MONTH_PAIR_FROM_THAN = "MONTH_PAIR_FROM_THAN"
    #: Theo **cung mộ của tam hợp chi năm**. Khớp lá số đối chiếu.
    YEAR_BRANCH_TRINE = "YEAR_BRANCH_TRINE"


#: Biến thể Giải Thần đang dùng.
#:
#: Chọn vì lá số đối chiếu **loại được** biến thể kia, không phải vì ai đã thẩm định
#: biến thể này. Một điểm dữ liệu bác bỏ được một luật nhưng không chứng minh được
#: luật còn lại, nên trạng thái vẫn là PROVISIONAL — xem docs mục 32.
SELECTED_GIAI_THAN_VARIANT = GiaiThanPolicy.YEAR_BRANCH_TRINE
