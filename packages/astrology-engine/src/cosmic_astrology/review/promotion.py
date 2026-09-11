"""Promoting a rule from PROVISIONAL to VERIFIED.

Never automatic. A passing test suite says the engine agrees with itself; only a
reviewer with a citation can say it agrees with the tradition. This module is the
gate, and it is designed to say no.
"""

from __future__ import annotations

from dataclasses import dataclass

from cosmic_astrology.conventions.policies import RuleId
from cosmic_astrology.conventions.profile import ConventionProfile
from cosmic_astrology.review.model import ReviewState
from cosmic_astrology.review.sources import SourceType
from cosmic_astrology.review.store import ReviewStore

__all__ = ["PromotionResult", "promote_rule_verification"]

#: Rules whose trust rests on the major-star fixture matrix.
_MATRIX_BACKED_RULES = frozenset({RuleId.TU_VI_PLACEMENT, RuleId.MAJOR_STARS})


@dataclass(frozen=True, slots=True)
class PromotionResult:
    rule: str
    granted: bool
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {"rule": self.rule, "granted": self.granted, "reasons": list(self.reasons)}


def promote_rule_verification(
    *,
    rule: RuleId,
    store: ReviewStore,
    profile: ConventionProfile,
    reviewer: str | None,
    source_id: str | None,
    evidence: str = "",
) -> PromotionResult:
    """Decide whether ``rule`` may be called VERIFIED. Does not mutate anything.

    Returning a refusal with reasons — rather than raising — lets the workbench
    show a reviewer exactly what is still missing.
    """
    reasons: list[str] = []

    if not reviewer:
        reasons.append("Thiếu người thẩm định.")
    if not source_id:
        reasons.append("Thiếu nguồn đối chiếu.")
    else:
        source = store.registry.get(source_id)
        if source is None:
            reasons.append(f"Nguồn '{source_id}' không có trong sổ nguồn.")
        elif not source.is_citable:
            reasons.append(f"Nguồn '{source_id}' chưa đủ thông tin để tra lại.")
        elif source.source_type is not SourceType.PRIMARY_SELECTED_REFERENCE:
            reasons.append(
                f"Nguồn '{source_id}' đang là {source.source_type.value}. Chỉ nguồn được "
                "chọn làm chuẩn (PRIMARY_SELECTED_REFERENCE) mới nâng được quy tắc."
            )
    if not evidence.strip():
        reasons.append("Thiếu mô tả bằng chứng (đã đối chiếu những ca nào, ở đâu).")

    binding = profile.binding(rule)
    if binding.is_unresolved:
        reasons.append(
            f"Quy ước '{rule.value}' còn UNRESOLVED (chờ {', '.join(binding.blocked_by)}) — "
            "chưa chốt luật thì không có gì để kiểm định."
        )
    if not binding.implemented:
        reasons.append(f"Quy tắc '{rule.value}' chưa được cài đặt.")

    if rule in _MATRIX_BACKED_RULES:
        states = store.states()
        unverified = [
            fid for fid, ev in states.items()
            if ev.state not in (ReviewState.VERIFIED, ReviewState.BLOCKED)
        ]
        disagreements = [
            fid for fid, ev in states.items() if ev.state is ReviewState.DISAGREEMENT
        ]
        verified = [fid for fid, ev in states.items() if ev.state is ReviewState.VERIFIED]

        if disagreements:
            reasons.append(
                f"Còn {len(disagreements)} ca bất đồng chưa giải quyết: "
                f"{', '.join(sorted(disagreements))}."
            )
        if unverified:
            reasons.append(
                f"Còn {len(unverified)} ca chưa thẩm định: {', '.join(sorted(unverified)[:5])}"
                + ("…" if len(unverified) > 5 else "")
            )
        if not verified:
            reasons.append("Chưa có ca nào được thẩm định.")

        blocking = [d for d in store.discrepancies if d.is_blocking]
        if blocking:
            reasons.append(
                f"Còn {len(blocking)} phiếu bất đồng đang mở: "
                f"{', '.join(d.id for d in blocking)}."
            )

    return PromotionResult(rule=rule.value, granted=not reasons, reasons=tuple(reasons))
