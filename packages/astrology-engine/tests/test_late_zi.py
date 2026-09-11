"""The late-Zi hour: the contradiction, made explicit.

Before the convention layer existed, a birth at 23:xx produced a chart whose day
pillar came from one civil day and whose star placement came from another —
because two modules had each quietly answered an open question, differently.
These tests pin down that the engine now either applies one named policy
consistently, or refuses.
"""

from __future__ import annotations

import pytest

from cosmic_astrology import BirthInput, build_chart
from cosmic_astrology.birth_moment import is_late_zi, resolve_birth_dates
from cosmic_astrology.chart.types import CalendarType, EngineStage, Gender
from cosmic_astrology.conventions import (
    COSMIC_SIGNS_STANDARD_V1,
    LateZiPolicy,
    RuleId,
    UnresolvedConventionError,
)

PROFILE = COSMIC_SIGNS_STANDARD_V1

#: The regression case from the audit: 10 September 1992, 23:00 local.
CASE = {"day": 10, "month": 9, "year": 1992}


def _birth(hour: int) -> BirthInput:
    return BirthInput(
        name="late-zi",
        gender=Gender.MALE,
        calendar_type=CalendarType.SOLAR,
        hour=hour,
        **CASE,  # type: ignore[arg-type]
    )


def _with(policy: LateZiPolicy):  # type: ignore[no-untyped-def]
    return PROFILE.with_rule(RuleId.LATE_ZI, policy=policy.value)


def test_only_2300_to_2359_is_the_disputed_hour() -> None:
    assert is_late_zi(23) is True
    assert [is_late_zi(h) for h in (0, 1, 22)] == [False, False, False]


def test_the_default_profile_refuses_rather_than_guessing() -> None:
    with pytest.raises(UnresolvedConventionError) as exc:
        build_chart(_birth(23), stage=EngineStage.PREVIEW)
    message = str(exc.value)
    assert "Q6" in message
    # The message has to name the alternatives, or the reader is stuck.
    for policy in ("CIVIL_DAY", "LATE_ZI_NEXT_DAY", "PILLAR_ONLY_NEXT_DAY"):
        assert policy in message


def test_an_unresolved_late_zi_rule_blocks_nothing_outside_that_hour() -> None:
    """22:00 and 00:00 are undisputed, so the open question must not block them."""
    for hour in (0, 12, 22):
        chart = build_chart(_birth(hour), stage=EngineStage.PREVIEW).to_dict()
        assert chart["date_resolution"]["late_zi"] is False
        assert chart["date_resolution"]["internally_consistent"] is True


@pytest.mark.parametrize(
    ("policy", "expect_consistent"),
    [
        (LateZiPolicy.CIVIL_DAY, True),
        (LateZiPolicy.LATE_ZI_NEXT_DAY, True),
        (LateZiPolicy.PILLAR_ONLY_NEXT_DAY, False),
    ],
)
def test_each_policy_states_whether_it_is_internally_consistent(
    policy: LateZiPolicy, expect_consistent: bool
) -> None:
    """PILLAR_ONLY_NEXT_DAY is asymmetric — that is now declared, not hidden."""
    dates = resolve_birth_dates(
        profile=_with(policy),
        calendar_is_lunar=False,
        hour=23,
        is_leap_month=False,
        tz_offset=7.0,
        **CASE,  # type: ignore[arg-type]
    )
    assert dates.late_zi is True
    assert dates.late_zi_policy == policy.value
    assert dates.is_internally_consistent is expect_consistent


def test_the_three_policies_do_not_agree_with_each_other() -> None:
    """If they agreed, there would be nothing to decide — and no risk."""
    results = {}
    for policy in LateZiPolicy:
        if policy is LateZiPolicy.UNRESOLVED:
            continue
        chart = build_chart(
            _birth(23), stage=EngineStage.PREVIEW, profile=_with(policy)
        ).to_dict()
        tu_vi = next(
            p["branch"]
            for p in chart["palaces"]
            for s in p["major_stars"]
            if s["id"] == "TU_VI"
        )
        results[policy.value] = (
            chart["lunar_birth"]["day"],
            chart["pillars"]["day"]["name"],
            tu_vi,
        )

    assert len(set(results.values())) == 3, f"các chính sách phải khác nhau: {results}"

    # The shape of the disagreement, recorded so a later refactor cannot blur it.
    civil = results["CIVIL_DAY"]
    next_day = results["LATE_ZI_NEXT_DAY"]
    pillar_only = results["PILLAR_ONLY_NEXT_DAY"]

    assert next_day[0] == civil[0] + 1, "LATE_ZI_NEXT_DAY phải đẩy ngày âm lên 1"
    assert pillar_only[0] == civil[0], "PILLAR_ONLY không được đổi ngày âm"
    assert pillar_only[1] == next_day[1], "PILLAR_ONLY phải dùng trụ ngày của ngày sau"
    assert pillar_only[2] == civil[2], "PILLAR_ONLY an sao theo ngày hiện tại"
    assert next_day[2] != civil[2], "đổi ngày âm phải làm Tử Vi dịch chỗ"


def test_the_old_hidden_behaviour_is_now_a_named_policy() -> None:
    """What the code used to do by accident is PILLAR_ONLY_NEXT_DAY.

    Kept as a regression anchor: it documents the pre-refactor behaviour without
    endorsing it as the production default.
    """
    chart = build_chart(
        _birth(23), stage=EngineStage.PREVIEW, profile=_with(LateZiPolicy.PILLAR_ONLY_NEXT_DAY)
    ).to_dict()
    assert chart["lunar_birth"]["day"] == 14
    assert chart["pillars"]["day"]["name"] == "Canh Dần"
    assert chart["date_resolution"]["internally_consistent"] is False
