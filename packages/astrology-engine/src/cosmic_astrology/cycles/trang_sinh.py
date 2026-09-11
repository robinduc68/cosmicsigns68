"""Vòng Tràng Sinh — the twelve life stages laid around the địa bàn.

Two school-dependent choices live here, and both are represented as convention
policies rather than hidden in the arithmetic:

1. **Where the cycle starts.** Taken from the ngũ hành of the Cục. Kim/Mộc/Thủy/Hỏa
   are read the same way everywhere; **Thổ is not** — most Vietnamese texts start it
   at Thân, following Thủy, while others start it at Dần, following Hỏa.
2. **Which way it runs.** Most texts tie it to âm dương of the year stem and the
   subject's gender, the same rule as đại vận. Others tie it to the âm dương of the
   Cục instead, which gives a different answer for half of all charts.

Nothing here picks a school. The policy on the active ``ConventionProfile`` does,
and the answer is stamped into every chart along with its verification status.
"""

from __future__ import annotations

from cosmic_astrology.calendar.sexagenary import CHI, Element
from cosmic_astrology.conventions.policies import TrangSinhDirectionPolicy, TrangSinhStartPolicy

__all__ = [
    "TRANG_SINH_STAGES",
    "runs_forward",
    "stage_by_branch",
    "start_branch",
]

#: The twelve stages, in cycle order from Tràng Sinh.
TRANG_SINH_STAGES: tuple[str, ...] = (
    "Tràng Sinh",
    "Mộc Dục",
    "Quan Đới",
    "Lâm Quan",
    "Đế Vượng",
    "Suy",
    "Bệnh",
    "Tử",
    "Mộ",
    "Tuyệt",
    "Thai",
    "Dưỡng",
)

#: Branch each element's cycle begins on, under ``CUC_ELEMENT_CLASSICAL``.
#: Thổ shares Thủy's starting branch here; see ``_THO_FOLLOWS_HOA`` for the other
#: reading, which this profile does not select.
_START_THO_WITH_THUY: dict[Element, int] = {
    Element.KIM: CHI.index("Tỵ"),
    Element.MOC: CHI.index("Hợi"),
    Element.THUY: CHI.index("Thân"),
    Element.HOA: CHI.index("Dần"),
    Element.THO: CHI.index("Thân"),
}

#: The competing reading, kept in code so the difference is inspectable rather than
#: a sentence in a document. Only Thổ differs.
_START_THO_WITH_HOA: dict[Element, int] = {**_START_THO_WITH_THUY, Element.THO: CHI.index("Dần")}

_START_TABLES: dict[str, dict[Element, int]] = {
    TrangSinhStartPolicy.CUC_ELEMENT_THO_WITH_THUY.value: _START_THO_WITH_THUY,
    TrangSinhStartPolicy.CUC_ELEMENT_THO_WITH_HOA.value: _START_THO_WITH_HOA,
}


def start_branch(cuc_element: Element, *, policy: str) -> int:
    """Branch index where Tràng Sinh sits for this Cục."""
    table = _START_TABLES.get(policy)
    if table is None:
        raise ValueError(f"Chưa biết cách khởi vòng Tràng Sinh cho quy tắc {policy!r}")
    return table[cuc_element]


def runs_forward(*, year_is_yang: bool, is_male: bool, cuc_is_yang: bool, policy: str) -> bool:
    """Whether the cycle runs with the địa chi (thuận) or against it (nghịch)."""
    if policy == TrangSinhDirectionPolicy.YANG_MALE_YIN_FEMALE_FORWARD.value:
        # Dương nam and âm nữ go thuận; âm nam and dương nữ go nghịch.
        return year_is_yang == is_male
    if policy == TrangSinhDirectionPolicy.CUC_POLARITY.value:
        return cuc_is_yang
    raise ValueError(f"Chưa biết chiều vòng Tràng Sinh cho quy tắc {policy!r}")


def stage_by_branch(start: int, *, forward: bool) -> dict[int, str]:
    """The stage sitting on each of the twelve branches.

    Keyed by branch index rather than by palace: the cycle is laid on the địa bàn,
    so it follows the branches and is unaffected by which palace name sits where.
    """
    step = 1 if forward else -1
    return {(start + step * i) % 12: stage for i, stage in enumerate(TRANG_SINH_STAGES)}
