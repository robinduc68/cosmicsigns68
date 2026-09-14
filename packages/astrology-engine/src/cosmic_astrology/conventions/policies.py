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
    STAR_ELEMENTS = "star_elements"
    FOUR_TRANSFORMATIONS = "four_transformations"
    TUAN = "tuan"
    TRIET = "triet"
    STAR_STRENGTH = "star_strength"
    TRANG_SINH_START = "trang_sinh_start"
    TRANG_SINH_DIRECTION = "trang_sinh_direction"
    MAJOR_CYCLE_DIRECTION = "major_cycle_direction"
    MAJOR_CYCLE_START_AGE = "major_cycle_start_age"


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

    Đếm thuận tới ngày sinh rồi **lùi một cung** — chỗ này có bản ghi khác.
    """

    FROM_XUONG_KHUC_BY_LUNAR_DAY_BACK_ONE = "FROM_XUONG_KHUC_BY_LUNAR_DAY_BACK_ONE"


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
