"""Optional derivation trace.

When a reviewer says "Thiên Lương is in the wrong palace", the useful reply is
not "that is what the code returns" but the chain that put it there: which rule,
under which convention, from which inputs, and how far that rule is trusted.

The trace is off by default and carries no cost when unused. It is a tool for
developers, reviewers and the astrologer signing off the fixture matrix — not
something end users see.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from cosmic_astrology.conventions.policies import RuleId
from cosmic_astrology.conventions.profile import ConventionProfile

__all__ = ["TraceEntry", "TraceLog"]


@dataclass(frozen=True, slots=True)
class TraceEntry:
    """One derivation step."""

    rule: RuleId
    result: str
    inputs: dict[str, object]
    policy: str
    verification: str
    blocked_by: tuple[str, ...]
    note: str

    def to_dict(self) -> dict[str, object]:
        return {
            "rule": self.rule.value,
            "result": self.result,
            "inputs": self.inputs,
            "policy": self.policy,
            "verification": self.verification,
            "blocked_by": list(self.blocked_by),
            "note": self.note,
        }

    def format(self) -> str:
        args = ", ".join(f"{k}={v}" for k, v in self.inputs.items())
        line = f"{self.rule.value} → {self.result}\n    vì: {args}\n    quy tắc: {self.policy}"
        line += f" · độ tin cậy: {self.verification}"
        if self.blocked_by:
            line += f" · chờ: {', '.join(self.blocked_by)}"
        if self.note:
            line += f"\n    ghi chú: {self.note}"
        return line


@dataclass(slots=True)
class TraceLog:
    """Collects derivation steps for one chart."""

    profile_id: str
    profile_version: str
    entries: list[TraceEntry] = field(default_factory=list)

    @classmethod
    def for_profile(cls, profile: ConventionProfile) -> TraceLog:
        return cls(profile_id=profile.profile_id, profile_version=profile.version)

    def record(
        self,
        profile: ConventionProfile,
        rule: RuleId,
        result: object,
        **inputs: object,
    ) -> None:
        binding = profile.binding(rule)
        self.entries.append(
            TraceEntry(
                rule=rule,
                result=str(result),
                inputs=inputs,
                policy=binding.policy,
                verification=binding.display_status,
                blocked_by=binding.blocked_by,
                note=binding.note,
            )
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "convention_profile": self.profile_id,
            "convention_version": self.profile_version,
            "steps": [e.to_dict() for e in self.entries],
        }

    def format(self) -> str:
        header = f"convention: {self.profile_id}@{self.profile_version}"
        return "\n".join([header, *(e.format() for e in self.entries)])
