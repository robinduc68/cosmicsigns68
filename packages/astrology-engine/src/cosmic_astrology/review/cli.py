"""Command line for the verification workbench.

Exists so a review pack can go out and come back without anyone running the web
application, and so promotion is a deliberate command rather than a side effect.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from cosmic_astrology.conventions.policies import RuleId
from cosmic_astrology.conventions.standard import COSMIC_SIGNS_STANDARD_V1
from cosmic_astrology.review.model import ReviewState
from cosmic_astrology.review.pack import apply_import, export_csv, export_json, preview_import
from cosmic_astrology.review.promotion import promote_rule_verification
from cosmic_astrology.review.store import load_store

__all__ = ["main"]

_STATE_MARK = {
    ReviewState.VERIFIED: "✓",
    ReviewState.DISAGREEMENT: "✗",
    ReviewState.BLOCKED: "⊘",
    ReviewState.IN_REVIEW: "…",
    ReviewState.PENDING: " ",
}


def _cmd_status() -> int:
    store = load_store()
    states = store.states()
    print(f"{'ID':8} {'trạng thái':14} chi tiết")
    print("-" * 78)
    for record in store.records:
        evaluation = states[record.id]
        detail = evaluation.blockers[0] if evaluation.blockers else ""
        if evaluation.mismatches:
            detail = f"lệch: {', '.join(evaluation.mismatches)}"
        mark = _STATE_MARK[evaluation.state]
        print(f"{record.id:8} {mark} {evaluation.state.value:12} {detail[:52]}")
    print()
    summary = store.summary()
    print(" · ".join(f"{k}: {v}" for k, v in summary.items()))
    primary = store.registry.primary
    print(f"Nguồn chuẩn đã chọn: {primary.id if primary else 'CHƯA CÓ'}")
    return 0


def _cmd_export(out_dir: Path) -> int:
    store = load_store()
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "cosmic-signs-review-pack.csv"
    json_path = out_dir / "cosmic-signs-review-pack.json"
    csv_path.write_text(export_csv(store), encoding="utf-8")
    json_path.write_text(export_json(store), encoding="utf-8")
    print(f"Đã xuất {len(store.records)} ca:")
    print(f"  {csv_path}")
    print(f"  {json_path}")
    print("Các cột expected_* để trống có chủ đích — đừng chép từ cột engine_*.")
    return 0


def _cmd_import(path: Path, *, apply: bool) -> int:
    store = load_store()
    outcome = preview_import(store, path.read_text(encoding="utf-8"))

    for fixture_id, review in outcome.accepted.items():
        print(
            f"  nhận   {fixture_id}  "
            f"(người thẩm định: {review.reviewer}, nguồn: {review.source_id})"
        )
    for reason in outcome.skipped:
        print(f"  bỏ qua {reason}")
    for reason in outcome.rejected:
        print(f"  TỪ CHỐI {reason}")

    if not outcome.is_clean:
        print("\nGói có dòng bị từ chối — không nhập gì cả. Sửa rồi chạy lại.")
        return 1
    if not apply:
        print(f"\nXem trước: sẽ cập nhật {len(outcome.accepted)} ca. Thêm --apply để ghi thật.")
        return 0

    applied = apply_import(store, outcome)
    for fixture_id, state in applied.items():
        print(f"  đã ghi {fixture_id} -> {state}")
    return 0


def _cmd_promote(rule_name: str, reviewer: str | None, source_id: str | None, evidence: str) -> int:
    try:
        rule = RuleId(rule_name)
    except ValueError:
        print(f"Không có quy tắc '{rule_name}'. Các giá trị hợp lệ: "
              + ", ".join(r.value for r in RuleId))
        return 2

    result = promote_rule_verification(
        rule=rule,
        store=load_store(),
        profile=COSMIC_SIGNS_STANDARD_V1,
        reviewer=reviewer,
        source_id=source_id,
        evidence=evidence,
    )
    if result.granted:
        print(f"Đủ điều kiện nâng '{rule.value}' lên VERIFIED.")
        print("Bước cuối là sửa RuleBinding trong conventions/standard.py — cố ý làm tay,")
        print("để việc nâng cấp luôn là một commit có người chịu trách nhiệm.")
        return 0

    print(f"CHƯA nâng được '{rule.value}':")
    for reason in result.reasons:
        print(f"  - {reason}")
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cosmic-review", description="Bàn làm việc kiểm định engine Tử Vi (nội bộ)"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Trạng thái từng ca kiểm định")

    export_parser = sub.add_parser("export", help="Xuất gói thẩm định (CSV + JSON)")
    export_parser.add_argument("--out", type=Path, default=Path("review-pack"))

    import_parser = sub.add_parser("import", help="Nhập gói thẩm định đã điền")
    import_parser.add_argument("path", type=Path)
    import_parser.add_argument(
        "--apply", action="store_true", help="Ghi thật (mặc định chỉ xem trước)"
    )

    promote_parser = sub.add_parser("promote", help="Kiểm tra điều kiện nâng một quy tắc")
    promote_parser.add_argument("rule")
    promote_parser.add_argument("--reviewer")
    promote_parser.add_argument("--source")
    promote_parser.add_argument("--evidence", default="")

    args = parser.parse_args(argv)
    if args.command == "status":
        return _cmd_status()
    if args.command == "export":
        return _cmd_export(args.out)
    if args.command == "import":
        return _cmd_import(args.path, apply=args.apply)
    return _cmd_promote(args.rule, args.reviewer, args.source, args.evidence)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
