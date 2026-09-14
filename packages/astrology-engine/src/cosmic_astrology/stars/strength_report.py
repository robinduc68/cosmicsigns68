"""Báo cáo độ phủ bảng độ sáng.

    python -m cosmic_astrology.stars.strength_report
    make astrology-star-strength-report

Chỉ để phát hiện ô còn thiếu. Mọi con số đếm từ bảng và từ tập sao engine thực sự
an, nên báo cáo không thể lệch khỏi dữ liệu nó mô tả.
"""

from __future__ import annotations

from cosmic_astrology.stars.catalog import definition_for
from cosmic_astrology.stars.strength import NAM_PHAI_STAR_STRENGTH_V1, strength_coverage

__all__ = ["main", "render_report"]


def _placed_star_ids() -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Mã sao engine thực sự an, tách chính tinh và phụ tinh.

    Nhập trong hàm để module báo cáo không kéo theo cả builder khi chỉ cần bảng.
    """
    from cosmic_astrology.chart.builder import (
        _SUPPORTING_GROUP_1,
        _THIEN_PHU_CHAIN,
        _TU_VI_CHAIN,
    )

    major = tuple(star_id for star_id, _ in (*_TU_VI_CHAIN, *_THIEN_PHU_CHAIN))
    minor = (*(entry[0] for entry in _SUPPORTING_GROUP_1), "KINH_DUONG", "DA_LA")
    return major, minor


def _name(star_id: str) -> str:
    definition = definition_for(star_id)
    return definition.vietnamese_name if definition else star_id


def render_report(*, limit: int = 24) -> str:
    table = NAM_PHAI_STAR_STRENGTH_V1
    major, minor = _placed_star_ids()

    major_cov = strength_coverage(table, major)
    minor_cov = strength_coverage(table, minor)
    all_cov = strength_coverage(table, (*major, *minor))

    lines = [
        "Cosmic Signs — độ phủ bảng Miếu / Vượng / Đắc / Bình / Hãm",
        "",
        f"Bảng   : {table.table_id}@{table.version}",
        f"Nguồn  : {table.source_title or 'CHƯA CHỌN'}"
        + (f", tr. {table.source_page}" if table.source_page else ""),
        f"Ký duyệt: {table.verified_by or 'CHƯA CÓ'}",
        "",
        f"Chính tinh : {major_cov.filled_cells}/{major_cov.total_cells} ô"
        f"  ({major_cov.percentage}%) — {len(major)} sao × 12 địa chi",
        f"Phụ tinh   : {minor_cov.filled_cells}/{minor_cov.total_cells} ô"
        f"  ({minor_cov.percentage}%) — {len(minor)} sao × 12 địa chi",
        f"Toàn bộ    : {all_cov.filled_cells}/{all_cov.total_cells} ô"
        f"  ({all_cov.percentage}%)",
        "",
    ]

    if table.is_empty:
        lines += [
            "BẢNG ĐANG RỖNG — đây là trạng thái đúng, không phải lỗi.",
            "",
            "168 ô của 14 chính tinh không suy ra được bằng công thức; phải chép từ một",
            "ấn bản cụ thể. Một bảng sai vẫn trông 'hợp lý' với người không rành, nên để",
            "trống an toàn hơn nhiều so với điền bừa.",
            "",
            "Điền vào: stars/data/nam_phai_star_strength_v1.json (xem _README trong file).",
            "Chặn bởi: Q2 (ấn bản) và Q3 (người thẩm định).",
        ]
        return "\n".join(lines)

    lines.append(f"Sao đã có bảng: {', '.join(_name(s) for s in all_cov.covered_stars) or '—'}")
    if all_cov.missing:
        lines += ["", f"Ô còn thiếu ({len(all_cov.missing)}):"]
        for star_id, branch in all_cov.missing[:limit]:
            lines.append(f"  {_name(star_id):<14} {branch}")
        if len(all_cov.missing) > limit:
            lines.append(f"  … và {len(all_cov.missing) - limit} ô nữa")
    else:
        lines += ["", "Không ô nào thiếu."]

    lines += [
        "",
        "Điền đủ KHÔNG tự động thành VERIFIED — việc nâng nhãn thuộc quy trình thẩm định.",
    ]
    return "\n".join(lines)


def main() -> int:
    print(render_report())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
