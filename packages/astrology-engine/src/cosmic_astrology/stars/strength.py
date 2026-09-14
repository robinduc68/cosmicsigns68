"""Bảng Miếu / Vượng / Đắc / Bình / Hãm.

**Không có công thức.** Bảng gồm 14 sao × 12 địa chi = 168 ô, khác nhau đáng kể
giữa các trường phái, và phải **chép từ nguồn** — xem ``docs/astrology-conventions.md``
§19. Vì thế module này chỉ làm ba việc: đọc bảng từ file dữ liệu, kiểm tính hợp lệ
của nó, và tra cứu. Nó không suy ra một ô nào.

Bảng nằm ở file JSON riêng chứ không nằm trong code, vì người điền nó là **người
thẩm định**, không phải người viết code. Đổi bảng không cần đụng tới engine.

Bảng hiện đang **rỗng**: chưa chọn ấn bản chuẩn (Q2) và chưa có người ký duyệt
(Q3). Mọi ``strength`` vì vậy là ``None``. Đó là trạng thái đúng, không phải lỗi —
một bảng miếu vượng sai trông vẫn "hợp lý" với người không rành, nên để trống an
toàn hơn nhiều so với điền bừa.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from cosmic_astrology.calendar.sexagenary import CHI
from cosmic_astrology.chart.types import StarStrength

__all__ = [
    "NAM_PHAI_STAR_STRENGTH_V1",
    "StarStrengthTable",
    "StrengthCoverage",
    "load_table",
    "strength_coverage",
]

_DATA_DIR = Path(__file__).parent / "data"
_NAM_PHAI_PATH = _DATA_DIR / "nam_phai_star_strength_v1.json"


@dataclass(frozen=True, slots=True)
class StarStrengthTable:
    """One school's strength table, with the provenance of the whole table.

    Provenance sits on the table rather than on each cell on purpose: a strength
    table is copied from one edition as a unit, and mixing rows from two editions
    is precisely what this project refuses to do.
    """

    table_id: str
    version: str
    #: Ấn bản đã chép bảng này ra. ``None`` khi chưa chọn nguồn.
    source_title: str | None
    source_page: str | None
    verified_by: str | None
    note: str
    #: ``{mã sao: {địa chi: độ sáng}}``. Thiếu ô nghĩa là **chưa biết**, không phải
    #: "bình hòa" — hai thứ đó khác nhau và không được lẫn.
    entries: Mapping[str, Mapping[str, StarStrength]]

    @property
    def is_empty(self) -> bool:
        return not self.entries

    @property
    def has_source(self) -> bool:
        return bool(self.source_title and self.verified_by)

    def strength_for(self, star_id: str, branch: str) -> StarStrength | None:
        """Độ sáng của một sao tại một địa chi, hoặc ``None`` khi bảng chưa có ô đó."""
        return self.entries.get(star_id, {}).get(branch)

    def covered_stars(self) -> tuple[str, ...]:
        return tuple(sorted(self.entries))


def _parse_entries(raw: object, table_id: str) -> Mapping[str, Mapping[str, StarStrength]]:
    """Đọc và **kiểm** bảng.

    Kiểm chặt có chủ ý: một ô gõ sai chính tả sẽ lặng lẽ thành "chưa biết" và không
    ai phát hiện. Thà hỏng lúc nạp còn hơn sai trên lá số của khách.
    """
    if not isinstance(raw, dict):
        raise ValueError(f"{table_id}: 'entries' phải là một object")

    valid_branches = set(CHI)
    valid_states = {s.value for s in StarStrength}
    parsed: dict[str, Mapping[str, StarStrength]] = {}

    for star_id, row in raw.items():
        if not isinstance(row, dict):
            raise ValueError(f"{table_id}/{star_id}: mỗi sao phải ứng với một object")
        cells: dict[str, StarStrength] = {}
        for branch, state in row.items():
            if branch not in valid_branches:
                raise ValueError(f"{table_id}/{star_id}: '{branch}' không phải địa chi")
            if state not in valid_states:
                raise ValueError(
                    f"{table_id}/{star_id}/{branch}: '{state}' không phải độ sáng hợp lệ "
                    f"({', '.join(sorted(valid_states))})"
                )
            cells[branch] = StarStrength(state)
        # Bất biến từ §19: một sao đã có bảng thì phải đủ 12 ô. Điền nửa vời là
        # cách "chưa biết" bị đọc thành "bình hòa".
        if cells and len(cells) != 12:
            missing = sorted(valid_branches - set(cells))
            raise ValueError(
                f"{table_id}/{star_id}: có {len(cells)}/12 địa chi, thiếu {', '.join(missing)}. "
                "Một sao đã vào bảng thì phải đủ 12 ô."
            )
        if cells:
            parsed[star_id] = MappingProxyType(cells)
    return MappingProxyType(parsed)


def load_table(path: Path) -> StarStrengthTable:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return StarStrengthTable(
        table_id=raw["table_id"],
        version=raw["version"],
        source_title=raw.get("source_title"),
        source_page=raw.get("source_page"),
        verified_by=raw.get("verified_by"),
        note=raw.get("note", ""),
        entries=_parse_entries(raw.get("entries", {}), raw["table_id"]),
    )


#: Bảng Nam phái. Hiện rỗng — chờ Q2 (ấn bản) và Q3 (người thẩm định).
NAM_PHAI_STAR_STRENGTH_V1 = load_table(_NAM_PHAI_PATH)


@dataclass(frozen=True, slots=True)
class StrengthCoverage:
    """Đếm từ bảng và từ lá số thật, không phải con số gõ tay."""

    total_cells: int
    filled_cells: int
    covered_stars: tuple[str, ...]
    #: ``(mã sao, địa chi)`` mà lá số cần nhưng bảng chưa có.
    missing: tuple[tuple[str, str], ...]

    @property
    def percentage(self) -> float:
        if self.total_cells == 0:
            return 0.0
        return round(self.filled_cells / self.total_cells * 100, 1)

    def to_dict(self) -> dict[str, object]:
        return {
            "total_cells": self.total_cells,
            "filled_cells": self.filled_cells,
            "percentage": self.percentage,
            "covered_stars": list(self.covered_stars),
            "missing": [list(m) for m in self.missing],
        }


def strength_coverage(
    table: StarStrengthTable, star_ids: tuple[str, ...]
) -> StrengthCoverage:
    """Độ phủ của bảng với một tập sao — ví dụ các sao engine thực sự an."""
    missing = tuple(
        (star_id, branch)
        for star_id in star_ids
        for branch in CHI
        if table.strength_for(star_id, branch) is None
    )
    total = len(star_ids) * 12
    return StrengthCoverage(
        total_cells=total,
        filled_cells=total - len(missing),
        covered_stars=table.covered_stars(),
        missing=missing,
    )
