"""Convention profiles: one immutable, versioned bundle of rule choices.

A chart is only meaningful together with the profile it was built under. The
profile id and version are stamped into every chart so that a later engine
change cannot quietly reinterpret an old one.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from types import MappingProxyType

from cosmic_astrology.conventions.policies import RuleId, VerificationStatus
from cosmic_astrology.conventions.provenance import SourceReference

__all__ = [
    "ConventionProfile",
    "ProfileValidation",
    "RecalculationCheck",
    "RuleBinding",
    "UnresolvedConventionError",
    "is_production_ready",
    "needs_recalculation",
    "validate_convention_profile",
]

UNRESOLVED = "UNRESOLVED"


class UnresolvedConventionError(RuntimeError):
    """Raised when a calculation needs a rule the active profile has not decided.

    This is the mechanism that keeps an open question from becoming an accidental
    default: the engine stops instead of picking a school on the caller's behalf.
    """


@dataclass(frozen=True, slots=True)
class RuleBinding:
    """One rule: which policy, how far it is trusted, and why."""

    rule: RuleId
    policy: str
    implemented: bool
    verification: VerificationStatus
    source: SourceReference
    #: Open-question ids (``"Q6"``…) that must be answered before this rule moves on.
    blocked_by: tuple[str, ...] = ()
    note: str = ""

    @property
    def is_unresolved(self) -> bool:
        return self.policy == UNRESOLVED

    @property
    def display_status(self) -> str:
        """Status as the verification report shows it.

        ``BLOCKED`` is not a verification level — it is the combination of "not
        implemented" and "waiting on an open question", which reads more clearly
        in a report than ``UNVERIFIED`` alone.
        """
        if not self.implemented and self.blocked_by:
            return "BLOCKED"
        return self.verification.value

    def to_dict(self) -> dict[str, object]:
        return {
            "rule": self.rule.value,
            "policy": self.policy,
            "implemented": self.implemented,
            "verification": self.verification.value,
            "status": self.display_status,
            "blocked_by": list(self.blocked_by),
            "source": self.source.to_dict(),
            "note": self.note,
        }


@dataclass(frozen=True, slots=True)
class ConventionProfile:
    """An immutable, versioned set of rule bindings."""

    profile_id: str
    version: str
    description: str
    rules: Mapping[RuleId, RuleBinding] = field(default_factory=dict)

    def __post_init__(self) -> None:
        missing = [r.value for r in RuleId if r not in self.rules]
        if missing:
            raise ValueError(
                "Hồ sơ quy ước thiếu quy tắc: "
                + ", ".join(sorted(missing))
                + ". Mọi quy tắc phụ thuộc trường phái đều phải được nêu tên."
            )
        for rule_id, binding in self.rules.items():
            if binding.rule is not rule_id:
                raise ValueError(f"Quy tắc {rule_id.value} gắn nhầm vào {binding.rule.value}")
        object.__setattr__(self, "rules", MappingProxyType(dict(self.rules)))

    def binding(self, rule: RuleId) -> RuleBinding:
        return self.rules[rule]

    def policy(self, rule: RuleId) -> str:
        """The selected policy, or raise if the profile has not decided."""
        binding = self.rules[rule]
        if binding.is_unresolved:
            blockers = ", ".join(binding.blocked_by) or "chưa xác định"
            raise UnresolvedConventionError(
                f"Quy ước '{rule.value}' chưa được chốt trong hồ sơ "
                f"{self.profile_id}@{self.version} (chờ: {blockers}). "
                f"{binding.note}".strip()
            )
        return binding.policy

    def require(self, rule: RuleId, *expected: str) -> str:
        """Assert the profile selected one of ``expected`` for ``rule``."""
        chosen = self.policy(rule)
        if chosen not in expected:
            raise UnresolvedConventionError(
                f"Quy ước '{rule.value}' đang đặt là '{chosen}', nhưng phần cài đặt "
                f"hiện tại chỉ hỗ trợ: {', '.join(expected)}."
            )
        return chosen

    def with_rule(self, rule: RuleId, **changes: object) -> ConventionProfile:
        """A copy with one binding altered — used by tests to explore policies.

        Profiles are immutable, so exploring an alternative never mutates the
        shared standard profile.
        """
        updated = dict(self.rules)
        updated[rule] = replace(updated[rule], **changes)  # type: ignore[arg-type]
        return ConventionProfile(
            profile_id=f"{self.profile_id}+{rule.value}",
            version=self.version,
            description=f"{self.description} (biến thể: {rule.value})",
            rules=updated,
        )

    @property
    def stamp(self) -> dict[str, str]:
        """Immutable metadata copied into every chart built under this profile."""
        return {"convention_profile": self.profile_id, "convention_version": self.version}

    def to_dict(self) -> dict[str, object]:
        return {
            "profile_id": self.profile_id,
            "version": self.version,
            "description": self.description,
            "rules": [self.rules[r].to_dict() for r in RuleId],
        }


#: Rules a chart cannot be sold on without. Everything else may lag behind.
CRITICAL_RULES: tuple[RuleId, ...] = (
    RuleId.CALENDAR,
    RuleId.TIMEZONE,
    RuleId.LATE_ZI,
    RuleId.MENH_PLACEMENT,
    RuleId.THAN_PLACEMENT,
    RuleId.CUC,
    RuleId.PALACE_ORDER,
    RuleId.PALACE_STEMS,
    RuleId.TU_VI_PLACEMENT,
    RuleId.MAJOR_STARS,
)


@dataclass(frozen=True, slots=True)
class ProfileValidation:
    profile_id: str
    version: str
    production_ready: bool
    failures: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "profile_id": self.profile_id,
            "version": self.version,
            "production_ready": self.production_ready,
            "failures": list(self.failures),
        }


def validate_convention_profile(profile: ConventionProfile) -> ProfileValidation:
    """Check a profile against the bar for producing charts shown to customers."""
    failures: list[str] = []
    for rule in CRITICAL_RULES:
        binding = profile.binding(rule)
        if binding.is_unresolved:
            blockers = ", ".join(binding.blocked_by) or "chưa xác định"
            failures.append(f"{rule.value}: chưa chốt quy ước (chờ {blockers})")
        elif not binding.implemented:
            failures.append(f"{rule.value}: chưa cài đặt")
        elif binding.verification is not VerificationStatus.VERIFIED:
            failures.append(f"{rule.value}: mới ở mức {binding.verification.value}")
    return ProfileValidation(
        profile_id=profile.profile_id,
        version=profile.version,
        production_ready=not failures,
        failures=tuple(failures),
    )


def is_production_ready(profile: ConventionProfile) -> bool:
    return validate_convention_profile(profile).production_ready


@dataclass(frozen=True, slots=True)
class RecalculationCheck:
    needed: bool
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {"needed": self.needed, "reason": self.reason}


def needs_recalculation(
    stored_profile: str | None,
    stored_version: str | None,
    current: ConventionProfile,
    *,
    stored_engine_version: str | None = None,
    current_engine_version: str | None = None,
) -> RecalculationCheck:
    """Whether a stored chart predates the conventions or the engine now in force.

    The engine version matters as much as the profile: a calculation bug fix keeps
    the same rules but changes the answer, and the charts already on disk keep the
    old one. Both versions are passed in rather than imported, so this module stays
    free of any dependency on the calculation layer.

    Charts are not recomputed on read: a reading a customer has already paid for
    must not change under them. This answers the migration question instead —
    which stored charts would come out differently today, so a deliberate
    re-run can be offered rather than imposed.
    """
    if stored_profile is None or stored_version is None:
        return RecalculationCheck(
            True, "Lá số lập trước khi có hồ sơ quy ước — không biết đã dùng luật nào."
        )
    if stored_profile != current.profile_id:
        return RecalculationCheck(
            True, f"Lập theo hồ sơ '{stored_profile}', hiện dùng '{current.profile_id}'."
        )
    if stored_version != current.version:
        return RecalculationCheck(
            True,
            f"Hồ sơ '{stored_profile}' đã lên phiên bản {current.version} "
            f"(lá số ở {stored_version}).",
        )
    if (
        stored_engine_version is not None
        and current_engine_version is not None
        and stored_engine_version != current_engine_version
    ):
        return RecalculationCheck(
            True,
            f"Lá số lập bằng engine {stored_engine_version}, hiện dùng "
            f"{current_engine_version}. Cùng bộ quy ước nhưng engine đã sửa lỗi "
            "tính toán, nên kết quả có thể khác.",
        )
    return RecalculationCheck(False, "Khớp hồ sơ quy ước và engine hiện hành.")
