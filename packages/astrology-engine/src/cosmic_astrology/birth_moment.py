"""Turning a birth moment into the dates the rest of the engine counts from.

This is where the late-Zi question lives. Giờ Tý runs 23:00–00:59, so a birth in
its first hour can be argued onto either civil day, and different schools do
argue differently. Two dates come out of this module:

``placement_solar``
    the date whose *lunar day* drives star placement (Tử Vi and everything that
    chains off it)
``day_pillar_solar``
    the date whose Julian day drives the *day pillar*

Before this module existed those two were decided in different files under
different assumptions, and a 23:00 birth silently mixed them. Now a profile has
to name a policy, and each policy states plainly what it does to both dates.
"""

from __future__ import annotations

from dataclasses import dataclass

from cosmic_astrology.calendar.lunar import (
    LunarDate,
    jd_from_solar,
    jd_to_solar,
    lunar_to_solar,
    solar_to_lunar,
)
from cosmic_astrology.conventions.policies import LateZiPolicy, RuleId
from cosmic_astrology.conventions.profile import ConventionProfile, UnresolvedConventionError

__all__ = ["ResolvedBirthDates", "is_late_zi", "resolve_birth_dates"]

#: The first half of giờ Tý: the hour that belongs to two civil days at once.
LATE_ZI_HOUR = 23


def is_late_zi(hour: int) -> bool:
    return hour == LATE_ZI_HOUR


@dataclass(frozen=True, slots=True)
class ResolvedBirthDates:
    """The dates every later calculation counts from, and how they were chosen."""

    civil_solar: tuple[int, int, int]
    placement_solar: tuple[int, int, int]
    day_pillar_solar: tuple[int, int, int]
    lunar: LunarDate
    late_zi: bool
    late_zi_policy: str

    @property
    def is_internally_consistent(self) -> bool:
        """True when both derived dates came from the same civil day.

        ``PILLAR_ONLY_NEXT_DAY`` is the one policy for which this is ``False`` —
        on purpose, and recorded, so the asymmetry can never again be mistaken
        for an oversight.
        """
        return self.placement_solar == self.day_pillar_solar

    def to_dict(self) -> dict[str, object]:
        return {
            "civil_solar": list(self.civil_solar),
            "placement_solar": list(self.placement_solar),
            "day_pillar_solar": list(self.day_pillar_solar),
            "late_zi": self.late_zi,
            "late_zi_policy": self.late_zi_policy,
            "internally_consistent": self.is_internally_consistent,
        }


def _next_day(solar: tuple[int, int, int]) -> tuple[int, int, int]:
    day, month, year = solar
    return jd_to_solar(jd_from_solar(day, month, year) + 1)


def resolve_birth_dates(
    *,
    profile: ConventionProfile,
    calendar_is_lunar: bool,
    day: int,
    month: int,
    year: int,
    hour: int,
    is_leap_month: bool,
    tz_offset: float,
) -> ResolvedBirthDates:
    """Resolve the civil, placement and day-pillar dates under ``profile``.

    Raises :class:`UnresolvedConventionError` for a late-Zi birth while the
    profile leaves the policy open — the engine stops rather than choosing a
    school on the caller's behalf.
    """
    if calendar_is_lunar:
        civil = lunar_to_solar(day, month, year, is_leap_month, tz_offset)
    else:
        civil = (day, month, year)

    late = is_late_zi(hour)

    if not late:
        # Outside the disputed hour every policy agrees, so the profile is not
        # consulted at all and an unresolved late-Zi rule blocks nothing.
        placement = day_pillar = civil
        policy_name = profile.binding(RuleId.LATE_ZI).policy
    else:
        binding = profile.binding(RuleId.LATE_ZI)
        if binding.is_unresolved:
            raise UnresolvedConventionError(
                f"Sinh lúc {hour}:xx rơi vào giờ Tý sớm, mà hồ sơ "
                f"{profile.profile_id}@{profile.version} chưa chốt quy ước "
                f"'{RuleId.LATE_ZI.value}' (chờ {', '.join(binding.blocked_by)}). "
                "Chọn một trong CIVIL_DAY / LATE_ZI_NEXT_DAY / PILLAR_ONLY_NEXT_DAY "
                "rồi lập lại — xem docs/astrology-conventions.md §3."
            )
        policy = LateZiPolicy(binding.policy)
        policy_name = policy.value
        if policy is LateZiPolicy.CIVIL_DAY:
            placement = day_pillar = civil
        elif policy is LateZiPolicy.LATE_ZI_NEXT_DAY:
            placement = day_pillar = _next_day(civil)
        else:  # PILLAR_ONLY_NEXT_DAY
            placement = civil
            day_pillar = _next_day(civil)

    if calendar_is_lunar and placement == civil:
        lunar = LunarDate(day=day, month=month, year=year, is_leap_month=is_leap_month)
    else:
        lunar = solar_to_lunar(*placement, tz_offset)

    return ResolvedBirthDates(
        civil_solar=civil,
        placement_solar=placement,
        day_pillar_solar=day_pillar,
        lunar=lunar,
        late_zi=late,
        late_zi_policy=policy_name,
    )
