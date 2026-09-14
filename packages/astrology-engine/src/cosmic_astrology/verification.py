"""Verification report — what the engine is actually allowed to claim.

Every number here is derived from the convention profile and the fixture matrix.
Nothing is hard-coded, so the report cannot drift away from reality: if a rule
is still provisional, the report says so whether or not anyone remembered to
update a document.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from cosmic_astrology.chart.model import StarCategory
from cosmic_astrology.conventions.nam_phai import COSMIC_SIGNS_NAM_PHAI_V1
from cosmic_astrology.conventions.policies import RuleId
from cosmic_astrology.conventions.profile import ConventionProfile, validate_convention_profile
from cosmic_astrology.stars.catalog import MetadataCoverage, metadata_coverage

__all__ = ["FixtureStats", "VerificationReport", "build_report", "render_report"]

_PACKAGE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE = _PACKAGE_ROOT / "tests" / "fixtures" / "major_stars_matrix.json"

#: Human labels for the report. Keys must stay in step with :class:`RuleId`.
_RULE_LABELS: dict[RuleId, str] = {
    RuleId.CALENDAR: "Calendar",
    RuleId.TIMEZONE: "Timezone",
    RuleId.BIRTH_TIME_CORRECTION: "Birth-time correction",
    RuleId.DAY_BOUNDARY: "Day boundary",
    RuleId.LATE_ZI: "Late Zi hour",
    RuleId.YIN_YANG: "Âm Dương",
    RuleId.MENH_PLACEMENT: "Mệnh",
    RuleId.THAN_PLACEMENT: "Thân",
    RuleId.CUC: "Cục",
    RuleId.PALACE_ORDER: "12-palace ordering",
    RuleId.PALACE_STEMS: "Ngũ Hổ Độn",
    RuleId.TU_VI_PLACEMENT: "Tử Vi placement",
    RuleId.MAJOR_STARS: "14 major stars",
    RuleId.VAN_XUONG_VAN_KHUC: "Văn Xương / Văn Khúc",
    RuleId.TA_PHU_HUU_BAT: "Tả Phù / Hữu Bật",
    RuleId.THIEN_KHOI_THIEN_VIET: "Thiên Khôi / Thiên Việt",
    RuleId.LOC_TON: "Lộc Tồn",
    RuleId.KINH_DUONG_DA_LA: "Kình Dương / Đà La",
    RuleId.DAO_HOA: "Đào Hoa",
    RuleId.HONG_LOAN_THIEN_HY: "Hồng Loan / Thiên Hỷ",
    RuleId.THIEN_MA: "Thiên Mã",
    RuleId.LONG_TRI_PHUONG_CAC: "Long Trì / Phượng Các",
    RuleId.TAM_THAI_BAT_TOA: "Tam Thai / Bát Tọa",
    RuleId.AN_QUANG_THIEN_QUY: "Ân Quang / Thiên Quý",
    RuleId.THIEN_DUC_NGUYET_DUC: "Thiên Đức / Nguyệt Đức",
    RuleId.THAI_TUE_CYCLE: "Vòng Thái Tuế (4 sao)",
    RuleId.HOA_CAI: "Hoa Cái",
    RuleId.THIEN_TAI_THIEN_THO: "Thiên Tài / Thiên Thọ",
    RuleId.STAR_ELEMENTS: "Ngũ hành của sao",
    RuleId.TUAN: "Tuần",
    RuleId.TRIET: "Triệt",
    RuleId.FOUR_TRANSFORMATIONS: "Four Transformations",
    RuleId.STAR_STRENGTH: "Star strength",
    RuleId.TRANG_SINH_START: "Tràng Sinh — khởi",
    RuleId.TRANG_SINH_DIRECTION: "Tràng Sinh — chiều",
    RuleId.MAJOR_CYCLE_DIRECTION: "Major-cycle direction",
    RuleId.MAJOR_CYCLE_START_AGE: "Major-cycle start age",
}


@dataclass(frozen=True, slots=True)
class FixtureStats:
    total: int
    verified: int
    pending: int
    in_review: int
    disagreement: int
    blocked: int
    source_of_truth: str

    def to_dict(self) -> dict[str, object]:
        return {
            "total": self.total,
            "verified": self.verified,
            "pending": self.pending,
            "in_review": self.in_review,
            "disagreement": self.disagreement,
            "blocked": self.blocked,
            "source_of_truth": self.source_of_truth,
        }


@dataclass(frozen=True, slots=True)
class VerificationReport:
    profile_id: str
    profile_version: str
    rules: tuple[tuple[str, str, tuple[str, ...]], ...]
    fixtures: FixtureStats
    elements: MetadataCoverage
    production_ready: bool
    failures: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "profile": self.profile_id,
            "version": self.profile_version,
            "rules": [
                {"label": label, "status": status, "blocked_by": list(blockers)}
                for label, status, blockers in self.rules
            ],
            "fixtures": self.fixtures.to_dict(),
            "star_metadata": self.elements.to_dict(),
            "production_ready": self.production_ready,
            "failures": list(self.failures),
        }


def _fixture_stats(path: Path) -> FixtureStats:
    """Counts derived from the review store, so they cannot drift from evidence."""
    if not path.exists():
        return FixtureStats(0, 0, 0, 0, 0, 0, "KHÔNG TÌM THẤY FILE FIXTURE")

    from cosmic_astrology.review.store import SOURCES_PATH, load_store

    store = load_store(path, SOURCES_PATH)
    counts = store.summary()
    return FixtureStats(
        total=counts["TOTAL"],
        verified=counts["VERIFIED"],
        pending=counts["PENDING"],
        in_review=counts["IN_REVIEW"],
        disagreement=counts["DISAGREEMENT"],
        blocked=counts["BLOCKED"],
        source_of_truth=str(store.data.get("source_of_truth", "CHƯA CHỐT")),
    )


def build_report(
    profile: ConventionProfile = COSMIC_SIGNS_NAM_PHAI_V1,
    fixture_path: Path = DEFAULT_FIXTURE,
) -> VerificationReport:
    validation = validate_convention_profile(profile)
    rules = tuple(
        (_RULE_LABELS[rule], profile.binding(rule).display_status, profile.binding(rule).blocked_by)
        for rule in RuleId
    )
    return VerificationReport(
        profile_id=profile.profile_id,
        profile_version=profile.version,
        rules=rules,
        fixtures=_fixture_stats(fixture_path),
        elements=metadata_coverage(),
        production_ready=validation.production_ready,
        failures=validation.failures,
    )


def render_report(report: VerificationReport) -> str:
    width = max(len(label) for label, _, _ in report.rules) + 2
    lines = [
        "Cosmic Signs — báo cáo kiểm định engine Tử Vi",
        f"Hồ sơ quy ước: {report.profile_id}@{report.profile_version}",
        "",
    ]
    for label, status, blockers in report.rules:
        suffix = f"   (chờ {', '.join(blockers)})" if blockers else ""
        lines.append(f"  {label:<{width}}{status}{suffix}")

    f = report.fixtures
    lines += [
        "",
        "Ma trận kiểm định 14 chính tinh:",
        f"  Nguồn chuẩn: {f.source_of_truth}",
        f"  Verified:     {f.verified}",
        f"  In review:    {f.in_review}",
        f"  Pending:      {f.pending}",
        f"  Disagreement: {f.disagreement}",
        f"  Blocked:      {f.blocked}",
        f"  Tổng:         {f.total}",
        "",
    ]

    major = report.elements.by_category(StarCategory.MAJOR)
    lines += [
        "Metadata sao (ngũ hành dùng để tô màu chữ):",
        f"  Chính tinh:   {major.with_element}/{major.total}  ({major.element_percentage}%)",
        f"  Tổng catalog: {report.elements.total} sao",
    ]
    if major.missing_element:
        lines.append(f"  Chưa có hành: {', '.join(major.missing_element)}")
        lines.append("                (các trường phái ghi khác nhau — vẽ bằng mực trung tính)")
    lines.append("  Chi tiết:     make astrology-star-metadata-report")
    lines += [
        "",
        f"Sẵn sàng cho production: {'CÓ' if report.production_ready else 'KHÔNG'}",
    ]
    for failure in report.failures:
        lines.append(f"  - {failure}")
    if not report.production_ready:
        lines += [
            "",
            "Đây là trạng thái đúng ở giai đoạn hiện tại, không phải lỗi.",
            "Xem docs/astrology-verification.md để biết cần làm gì tiếp.",
        ]
    return "\n".join(lines)


def main() -> int:
    print(render_report(build_report()))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
