"""Convention profiles: completeness, immutability, versioning, readiness."""

from __future__ import annotations

import pytest

from cosmic_astrology import ENGINE_VERSION, BirthInput, build_chart
from cosmic_astrology.chart.types import CalendarType, EngineStage, Gender
from cosmic_astrology.conventions import (
    COSMIC_SIGNS_NAM_PHAI_V1,
    ConventionProfile,
    RuleId,
    UnresolvedConventionError,
    VerificationStatus,
    is_production_ready,
    needs_recalculation,
    validate_convention_profile,
)
from cosmic_astrology.conventions.profile import CRITICAL_RULES, RuleBinding
from cosmic_astrology.conventions.provenance import NO_SOURCE_YET

#: Hồ sơ engine đang thực sự dùng. Đổi sang Nam phái cùng lúc với engine, nếu
#: không thì bộ test sẽ kiểm một hồ sơ không ai chạy.
PROFILE = COSMIC_SIGNS_NAM_PHAI_V1


def _birth(**over: object) -> BirthInput:
    base: dict[str, object] = {
        "name": "x",
        "gender": Gender.MALE,
        "calendar_type": CalendarType.SOLAR,
        "day": 10,
        "month": 9,
        "year": 1992,
        "hour": 14,
    }
    base.update(over)
    return BirthInput(**base)  # type: ignore[arg-type]


def test_a_profile_must_name_every_rule() -> None:
    """A rule left out of a profile is a rule hiding in the code again."""
    incomplete = {RuleId.CALENDAR: PROFILE.binding(RuleId.CALENDAR)}
    with pytest.raises(ValueError, match="thiếu quy tắc"):
        ConventionProfile(profile_id="X", version="1", description="", rules=incomplete)


def test_a_binding_cannot_be_filed_under_the_wrong_rule() -> None:
    rules = dict(PROFILE.rules)
    rules[RuleId.TUAN] = PROFILE.binding(RuleId.TRIET)
    with pytest.raises(ValueError, match="gắn nhầm"):
        ConventionProfile(profile_id="X", version="1", description="", rules=rules)


def test_profiles_are_immutable() -> None:
    with pytest.raises(TypeError):
        PROFILE.rules[RuleId.CALENDAR] = PROFILE.binding(RuleId.TUAN)  # type: ignore[index]


def test_exploring_a_variant_does_not_mutate_the_shared_profile() -> None:
    before = PROFILE.binding(RuleId.LATE_ZI).policy
    variant = PROFILE.with_rule(RuleId.LATE_ZI, policy="CIVIL_DAY")
    assert variant.binding(RuleId.LATE_ZI).policy == "CIVIL_DAY"
    assert PROFILE.binding(RuleId.LATE_ZI).policy == before == "UNRESOLVED"


def test_asking_for_an_unresolved_policy_raises_with_the_open_question() -> None:
    with pytest.raises(UnresolvedConventionError) as exc:
        PROFILE.policy(RuleId.STAR_STRENGTH)
    assert "Q1" in str(exc.value)


def test_implemented_and_verified_are_not_the_same_thing() -> None:
    """The 14 major stars are fully coded and still not trusted."""
    stars = PROFILE.binding(RuleId.MAJOR_STARS)
    assert stars.implemented is True
    assert stars.verification is VerificationStatus.PROVISIONAL
    assert stars.blocked_by


def test_blocked_rules_report_as_blocked_not_merely_unverified() -> None:
    for rule in (RuleId.FOUR_TRANSFORMATIONS, RuleId.STAR_STRENGTH):
        binding = PROFILE.binding(rule)
        assert binding.implemented is False
        assert binding.display_status == "BLOCKED"


def test_the_standard_profile_is_honest_about_not_being_production_ready() -> None:
    result = validate_convention_profile(PROFILE)
    assert result.production_ready is False
    assert is_production_ready(PROFILE) is False
    # The reasons must name the rules, so nobody has to guess what to fix.
    joined = " ".join(result.failures)
    assert RuleId.LATE_ZI.value in joined
    assert RuleId.MAJOR_STARS.value in joined


def test_a_fully_verified_profile_would_pass_the_gate() -> None:
    """The gate must be able to say yes, or it is not a gate but a wall."""
    rules = dict(PROFILE.rules)
    for rule in CRITICAL_RULES:
        rules[rule] = RuleBinding(
            rule=rule,
            policy="ANY_RESOLVED_POLICY",
            implemented=True,
            verification=VerificationStatus.VERIFIED,
            source=NO_SOURCE_YET,
        )
    ready = ConventionProfile(
        profile_id="TEST_ALL_VERIFIED", version="0", description="", rules=rules
    )
    assert is_production_ready(ready) is True


def test_every_chart_carries_the_profile_it_was_built_under() -> None:
    chart = build_chart(_birth(), stage=EngineStage.PREVIEW).to_dict()
    engine = chart["engine"]
    assert engine["convention_profile"] == PROFILE.profile_id
    assert engine["convention_version"] == PROFILE.version
    assert chart["convention"]["profile"] == PROFILE.profile_id
    assert chart["convention"]["version"] == PROFILE.version


def test_a_chart_records_the_rules_in_force_so_it_can_be_re_read_later() -> None:
    """Without this, a future engine change silently reinterprets old charts."""
    chart = build_chart(_birth(), stage=EngineStage.PREVIEW).to_dict()
    recorded = {r["rule"] for r in chart["convention"]["rules"]}
    assert recorded == {r.value for r in RuleId}


def test_charts_built_under_different_profiles_are_distinguishable() -> None:
    variant = PROFILE.with_rule(RuleId.LATE_ZI, policy="CIVIL_DAY")
    a = build_chart(_birth(), stage=EngineStage.PREVIEW).to_dict()
    b = build_chart(_birth(), stage=EngineStage.PREVIEW, profile=variant).to_dict()
    assert a["convention"]["profile"] != b["convention"]["profile"]


def test_trace_is_off_by_default_and_explains_placement_when_on() -> None:
    """A reviewer asking "why is this star here" needs more than the answer."""
    plain = build_chart(_birth(), stage=EngineStage.PREVIEW).to_dict()
    assert "trace" not in plain

    traced = build_chart(_birth(), stage=EngineStage.PREVIEW, trace=True).to_dict()
    steps = traced["trace"]["steps"]
    assert traced["trace"]["convention_profile"] == PROFILE.profile_id

    tu_vi = next(s for s in steps if s["rule"] == RuleId.TU_VI_PLACEMENT.value)
    assert tu_vi["inputs"]["cuc"] == 4
    assert tu_vi["inputs"]["lunar_day"] == 14
    assert tu_vi["verification"] == "PROVISIONAL"
    assert tu_vi["blocked_by"]

    # Every major star must be traceable back to which chain placed it.
    placements = [s for s in steps if s["rule"] == RuleId.MAJOR_STARS.value]
    assert len(placements) == 14
    assert {s["inputs"]["chain"] for s in placements} == {"Tử Vi", "Thiên Phủ"}


def test_tracing_does_not_change_the_chart() -> None:
    without = build_chart(_birth(), stage=EngineStage.PREVIEW).to_dict()
    with_trace = build_chart(_birth(), stage=EngineStage.PREVIEW, trace=True).to_dict()
    del with_trace["trace"]
    assert without == with_trace


def test_a_chart_from_an_older_engine_is_flagged_for_recalculation() -> None:
    """A bug fix keeps the same rules but changes the answer.

    Charts already on disk keep the old answer, so the engine version has to be
    part of the check — the palace-name inversion fixed in engine 0.2.0 is exactly
    this case.
    """
    check = needs_recalculation(
        PROFILE.profile_id,
        PROFILE.version,
        PROFILE,
        stored_engine_version="0.1.0-frame",
        current_engine_version="0.2.0-frame",
    )
    assert check.needed is True
    assert "0.1.0-frame" in check.reason


def test_a_chart_from_the_current_engine_and_profile_is_left_alone() -> None:
    check = needs_recalculation(
        PROFILE.profile_id,
        PROFILE.version,
        PROFILE,
        stored_engine_version=ENGINE_VERSION,
        current_engine_version=ENGINE_VERSION,
    )
    assert check.needed is False


def test_the_profile_check_still_wins_over_the_engine_check() -> None:
    """An unknown profile is the more serious finding, and is reported first."""
    check = needs_recalculation(
        None,
        None,
        PROFILE,
        stored_engine_version=ENGINE_VERSION,
        current_engine_version=ENGINE_VERSION,
    )
    assert check.needed is True
    assert "hồ sơ quy ước" in check.reason


def test_an_unknown_engine_version_does_not_raise_a_false_alarm() -> None:
    """Nothing is claimed when the caller cannot supply the versions."""
    assert needs_recalculation(PROFILE.profile_id, PROFILE.version, PROFILE).needed is False
