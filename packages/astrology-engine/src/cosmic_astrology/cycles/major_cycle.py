"""Đại vận — the ten-year cycles walked around the địa bàn from cung Mệnh.

Three facts, kept apart on purpose:

* **Direction** is school-dependent and is a convention policy.
* **The first cycle's age** is the Cục number, which the sources agree on.
* **What "age" counts** — tuổi ta or completed years — is open question Q11 and is
  *not* answered here. The numbers below are ages in whichever reckoning that
  question settles on; they are identical either way. Converting an age to a
  calendar year does depend on the answer, which is why lưu niên is still blocked.

Đại vận traversal direction is **not** the palace order. The twelve palace names
are fixed by ``PALACE_ORDER`` and never reverse; only the walk does. Conflating the
two produced the mirrored-palace bug fixed in engine 0.2.0, and this module works
in branch indices so the two cannot be confused again.
"""

from __future__ import annotations

from dataclasses import dataclass

from cosmic_astrology.conventions.policies import MajorCycleDirectionPolicy

__all__ = ["PALACE_SPAN_YEARS", "MajorCycle", "major_cycles", "runs_forward"]

#: Every đại vận covers ten years. Not school-dependent.
PALACE_SPAN_YEARS = 10


@dataclass(frozen=True, slots=True)
class MajorCycle:
    """One đại vận: which palace it falls on and the ages it covers."""

    #: 1-based; đại vận 1 is the one starting at cung Mệnh.
    index: int
    branch_index: int
    age_start: int
    age_end: int


def runs_forward(*, year_is_yang: bool, is_male: bool, policy: str) -> bool:
    if policy == MajorCycleDirectionPolicy.YANG_MALE_YIN_FEMALE_FORWARD.value:
        return year_is_yang == is_male
    raise ValueError(f"Chưa biết chiều đại vận cho quy tắc {policy!r}")


def major_cycles(
    *, menh_branch: int, cuc_number: int, forward: bool, count: int = 12
) -> tuple[MajorCycle, ...]:
    """The đại vận sequence, starting at cung Mệnh at the Cục number.

    Twelve cycles by default — one per palace, covering the Cục number through
    roughly 120. Nothing is truncated to a life expectancy; that is a judgement the
    engine has no business making.
    """
    step = 1 if forward else -1
    return tuple(
        MajorCycle(
            index=i + 1,
            branch_index=(menh_branch + step * i) % 12,
            age_start=cuc_number + i * PALACE_SPAN_YEARS,
            age_end=cuc_number + (i + 1) * PALACE_SPAN_YEARS - 1,
        )
        for i in range(count)
    )
