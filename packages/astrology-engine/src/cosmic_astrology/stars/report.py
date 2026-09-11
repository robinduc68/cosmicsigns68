"""Star metadata coverage report.

    python -m cosmic_astrology.stars.report        # or: make astrology-star-metadata-report

Every number is counted from the catalogue at run time. Nothing here is written
down by hand, so the report cannot quietly drift away from the data it describes —
which is the whole reason it exists.
"""

from __future__ import annotations

import json
import sys

from cosmic_astrology.chart.model import StarCategory
from cosmic_astrology.conventions.policies import VerificationStatus
from cosmic_astrology.stars.catalog import STAR_CATALOG, CategoryCoverage, metadata_coverage

__all__ = ["main", "render_report"]

#: Rows the report always prints, even at 0/0 — an empty category is a fact worth
#: seeing. `OTHER` is only printed when something has landed in it.
_ALWAYS_SHOWN: tuple[tuple[StarCategory, str], ...] = (
    (StarCategory.MAJOR, "Chính tinh"),
    (StarCategory.SUPPORTING, "Phụ tinh — cát"),
    (StarCategory.MALEFIC, "Phụ tinh — sát"),
    (StarCategory.LITERARY, "Phụ tinh — văn"),
    (StarCategory.ROMANCE, "Phụ tinh — đào hoa"),
    (StarCategory.WEALTH, "Phụ tinh — tài lộc"),
    (StarCategory.TRANSFORMATION, "Tứ Hóa"),
    (StarCategory.ANNUAL, "Lưu tinh"),
)


def _bar(row: CategoryCoverage, label: str) -> list[str]:
    lines = [
        f"  {label}",
        f"    Ngũ hành : {row.with_element}/{row.total}"
        + (f"  ({row.element_percentage}%)" if row.total else ""),
        f"    Âm dương : {row.with_polarity}/{row.total}"
        + (f"  ({row.polarity_percentage}%)" if row.total else ""),
    ]
    if row.total == 0:
        lines.append("    (chưa có sao nào thuộc loại này trong catalog)")
    return lines


def render_report() -> str:
    coverage = metadata_coverage()
    lines = [
        "Cosmic Signs — độ phủ metadata sao",
        "",
        f"Tổng số sao trong catalog: {coverage.total}",
        "",
    ]

    for category, label in _ALWAYS_SHOWN:
        lines += _bar(coverage.by_category(category), label)
        lines.append("")

    other = coverage.by_category(StarCategory.OTHER)
    if other.total:
        lines += _bar(other, "Chưa phân loại")
        lines.append("")

    missing_element = [
        (d.vietnamese_name, d.alternatives)
        for d in STAR_CATALOG.values()
        if not d.has_element
    ]
    if missing_element:
        lines.append("Chưa có ngũ hành / âm dương:")
        for name, alternatives in missing_element:
            lines.append(f"  - {name}")
            for alternative in alternatives:
                lines.append(f"      cách đọc khác: {alternative}")
        lines.append("")
    else:
        lines += ["Mọi sao trong catalog đều có ngũ hành và âm dương.", ""]

    # The provenance gap is the point of the whole report: values recorded from
    # common usage are not the same thing as values traced to a chosen edition.
    uncited = [d.vietnamese_name for d in STAR_CATALOG.values() if not d.provenance.has_citation]
    unreviewed = [d.vietnamese_name for d in STAR_CATALOG.values() if not d.provenance.is_reviewed]
    verified = [
        d.vietnamese_name
        for d in STAR_CATALOG.values()
        if d.verification_status is VerificationStatus.VERIFIED
    ]
    lines += [
        "Nguồn và kiểm định:",
        f"  Đã VERIFIED           : {len(verified)}/{coverage.total}",
        f"  Chưa có trích dẫn     : {len(uncited)}/{coverage.total}",
        f"  Chưa có người ký duyệt: {len(unreviewed)}/{coverage.total}",
    ]
    if uncited:
        lines += [
            "",
            "  Chưa chọn ấn bản chuẩn (Q1/Q2/Q3), nên không mục nào truy được về một",
            "  nguồn cụ thể. Các giá trị đang có ghi theo chỗ các bản đọc trùng nhau và",
            "  chỉ ở mức PROVISIONAL — xem docs/astrology-conventions.md mục 23.",
        ]
    return "\n".join(lines)


def main() -> int:
    if "--json" in sys.argv[1:]:
        print(json.dumps(metadata_coverage().to_dict(), ensure_ascii=False, indent=2))
        return 0
    print(render_report())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
