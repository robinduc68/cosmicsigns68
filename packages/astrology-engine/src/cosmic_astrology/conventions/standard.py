"""COSMIC_SIGNS_STANDARD_V1 — the profile the engine ships with today.

Read this file as a status report, not as a settled tradition. Several rules are
deliberately ``UNRESOLVED``; the engine refuses to apply them rather than
guessing. Every ``blocked_by`` entry points at a question in
``docs/astrology-conventions.md``.
"""

from __future__ import annotations

from cosmic_astrology.conventions.policies import (
    BirthTimeCorrectionPolicy,
    CalendarPolicy,
    CucPolicy,
    DayBoundaryPolicy,
    FourTransformationsPolicy,
    LateZiPolicy,
    MajorCycleDirectionPolicy,
    MajorCycleStartAgePolicy,
    MajorStarPolicy,
    MenhPolicy,
    PalaceOrderPolicy,
    PalaceStemPolicy,
    RuleId,
    StarStrengthPolicy,
    ThanPolicy,
    TimezonePolicy,
    TrietPolicy,
    TuanPolicy,
    TuViPolicy,
    VerificationStatus,
    YinYangPolicy,
)
from cosmic_astrology.conventions.profile import ConventionProfile, RuleBinding
from cosmic_astrology.conventions.provenance import NO_SOURCE_YET, SourceReference

__all__ = ["COSMIC_SIGNS_STANDARD_V1", "STANDARD_PROFILE_ID", "STANDARD_PROFILE_VERSION"]

STANDARD_PROFILE_ID = "COSMIC_SIGNS_STANDARD_V1"
STANDARD_PROFILE_VERSION = "2026.09"

V = VerificationStatus

#: Rules proven by the engine's own test suite against outside anchors (official
#: Tết dates, the Quý Mão 2023 leap month). Those anchors are public record, so
#: they stand on their own without waiting for Q1–Q3.
_SELF_VERIFIED = SourceReference(
    note=(
        "Kiểm chứng bằng bộ test của engine, đối chiếu mốc công khai "
        "(ngày Tết chính thống 2000–2026, tháng nhuận Quý Mão 2023)."
    )
)


def _rule(
    rule: RuleId,
    policy: str,
    *,
    implemented: bool,
    verification: VerificationStatus,
    source: SourceReference = NO_SOURCE_YET,
    blocked_by: tuple[str, ...] = (),
    note: str = "",
) -> tuple[RuleId, RuleBinding]:
    return rule, RuleBinding(
        rule=rule,
        policy=policy,
        implemented=implemented,
        verification=verification,
        source=source,
        blocked_by=blocked_by,
        note=note,
    )


COSMIC_SIGNS_STANDARD_V1 = ConventionProfile(
    profile_id=STANDARD_PROFILE_ID,
    version=STANDARD_PROFILE_VERSION,
    description=(
        "Hồ sơ quy ước mặc định của Cosmic Signs. Phần khung lá số đã kiểm chứng; "
        "phần an sao còn ở mức tạm; vài quy ước chưa chốt và engine sẽ dừng thay vì đoán."
    ),
    rules=dict(
        [
            _rule(
                RuleId.CALENDAR,
                CalendarPolicy.MEEUS_CH49_VIETNAM.value,
                implemented=True,
                verification=V.VERIFIED,
                source=_SELF_VERIFIED,
                note="Meeus ch.49 đầy đủ + hiệu chỉnh ΔT. Bản rút gọn sai tới ~43 phút.",
            ),
            _rule(
                RuleId.TIMEZONE,
                TimezonePolicy.IANA_HISTORICAL.value,
                implemented=True,
                verification=V.VERIFIED,
                source=SourceReference(
                    title="IANA Time Zone Database", note="Qua zoneinfo + gói tzdata"
                ),
                note=(
                    "Offset lấy theo thời điểm sinh, không cố định +7. "
                    "Miền Nam dùng UTC+8 giai đoạn 1960–1975 theo tzdb."
                ),
            ),
            _rule(
                RuleId.BIRTH_TIME_CORRECTION,
                BirthTimeCorrectionPolicy.NONE.value,
                implemented=True,
                verification=V.UNVERIFIED,
                blocked_by=("Q4",),
                note=(
                    "Hiện dùng giờ đồng hồ dân sự. Q4 hỏi có nên hiệu chỉnh về giờ mặt "
                    "trời thật không — chưa cài TRUE_SOLAR_TIME vì quy ước chưa định nghĩa."
                ),
            ),
            _rule(
                RuleId.DAY_BOUNDARY,
                DayBoundaryPolicy.LOCAL_MIDNIGHT.value,
                implemented=True,
                verification=V.VERIFIED,
                source=_SELF_VERIFIED,
                note="Ngày âm bắt đầu từ nửa đêm dân sự địa phương.",
            ),
            _rule(
                RuleId.LATE_ZI,
                LateZiPolicy.UNRESOLVED.value,
                implemented=True,
                verification=V.UNVERIFIED,
                blocked_by=("Q6",),
                note=(
                    "Ba phương án CIVIL_DAY / LATE_ZI_NEXT_DAY / PILLAR_ONLY_NEXT_DAY đều "
                    "có trường phái theo. Engine từ chối lập lá số sinh lúc 23:xx cho tới "
                    "khi chốt, thay vì âm thầm chọn hộ."
                ),
            ),
            _rule(
                RuleId.YIN_YANG,
                YinYangPolicy.YEAR_STEM_PARITY.value,
                implemented=True,
                verification=V.VERIFIED,
                source=_SELF_VERIFIED,
            ),
            _rule(
                RuleId.MENH_PLACEMENT,
                MenhPolicy.DAN_FORWARD_MONTH_BACKWARD_HOUR.value,
                implemented=True,
                verification=V.VERIFIED,
                source=_SELF_VERIFIED,
                note="Cách xử lý tháng nhuận khi đếm vẫn còn là câu hỏi mở.",
            ),
            _rule(
                RuleId.THAN_PLACEMENT,
                ThanPolicy.DAN_FORWARD_MONTH_FORWARD_HOUR.value,
                implemented=True,
                verification=V.VERIFIED,
                source=_SELF_VERIFIED,
            ),
            _rule(
                RuleId.CUC,
                CucPolicy.NAP_AM_OF_MENH_PALACE.value,
                implemented=True,
                verification=V.VERIFIED,
                source=_SELF_VERIFIED,
            ),
            _rule(
                RuleId.PALACE_ORDER,
                PalaceOrderPolicy.COUNTER_CLOCKWISE_FROM_MENH.value,
                implemented=True,
                verification=V.VERIFIED,
                source=_SELF_VERIFIED,
                note="Thứ tự cố định, không đảo theo giới tính.",
            ),
            _rule(
                RuleId.PALACE_STEMS,
                PalaceStemPolicy.NGU_HO_DON.value,
                implemented=True,
                verification=V.VERIFIED,
                source=_SELF_VERIFIED,
            ),
            _rule(
                RuleId.TU_VI_PLACEMENT,
                TuViPolicy.CUC_REMAINDER_CLASSICAL.value,
                implemented=True,
                verification=V.PROVISIONAL,
                blocked_by=("Q1", "Q2", "Q3"),
                note=(
                    "Khớp 5 mốc mùng 1 kinh điển, nhưng mới phủ 5/150 ô của bảng "
                    "cục × ngày. Chờ nguồn chuẩn và người thẩm định."
                ),
            ),
            _rule(
                RuleId.MAJOR_STARS,
                MajorStarPolicy.TWO_CHAINS_CLASSICAL.value,
                implemented=True,
                verification=V.PROVISIONAL,
                blocked_by=("Q1", "Q2", "Q3"),
                note="14 chính tinh đã an nhưng chưa có ca nào được ký duyệt.",
            ),
            _rule(
                RuleId.TUAN,
                TuanPolicy.YEAR_PILLAR_DECADE.value,
                implemented=True,
                verification=V.PROVISIONAL,
                blocked_by=("Q2",),
            ),
            _rule(
                RuleId.TRIET,
                TrietPolicy.YEAR_STEM_TABLE_EQUAL_WEIGHT.value,
                implemented=True,
                verification=V.PROVISIONAL,
                blocked_by=("Q2", "Q10"),
                note="Q10: hai cung bị triệt có cùng mức độ hay không.",
            ),
            _rule(
                RuleId.FOUR_TRANSFORMATIONS,
                FourTransformationsPolicy.UNRESOLVED.value,
                implemented=False,
                verification=V.UNVERIFIED,
                blocked_by=("Q7", "Q8", "Q9"),
                note=(
                    "Hàng Canh có ít nhất 3 biến thể; hàng Mậu và Nhâm khác nhau ở Hóa Khoa. "
                    "Ngoài ra còn phụ thuộc Văn Xương, Văn Khúc, Tả Phù, Hữu Bật — đều chưa cài."
                ),
            ),
            _rule(
                RuleId.STAR_STRENGTH,
                StarStrengthPolicy.UNRESOLVED.value,
                implemented=False,
                verification=V.UNVERIFIED,
                blocked_by=("Q1", "Q2", "Q3"),
                note=(
                    "Bảng 14 sao × 12 cung = 168 ô, không suy ra được bằng công thức. "
                    "Cố ý KHÔNG có giá trị mặc định nào."
                ),
            ),
            _rule(
                RuleId.MAJOR_CYCLE_DIRECTION,
                MajorCycleDirectionPolicy.YANG_MALE_YIN_FEMALE_FORWARD.value,
                implemented=True,
                verification=V.PROVISIONAL,
                blocked_by=("Q2",),
                note="Cờ is_thuan_ly đã tính; chưa dựng danh sách đại vận.",
            ),
            _rule(
                RuleId.MAJOR_CYCLE_START_AGE,
                MajorCycleStartAgePolicy.UNRESOLVED.value,
                implemented=False,
                verification=V.UNVERIFIED,
                blocked_by=("Q11", "Q12"),
                note="Chưa chốt tuổi ta hay tuổi tròn.",
            ),
        ]
    ),
)
