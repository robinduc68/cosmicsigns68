"""Bằng chứng đọc từ lá số đối chiếu, và cái chốt dùng nó để kiểm bảng.

Tách hẳn khỏi ``strength.py``: ở đó là **luật** (bảng một trường phái ghi ra), ở đây
là **quan sát** (những ô ta đọc được từ một lá số chuẩn có thật). Trộn hai thứ vào
một chỗ là cách "chúng tôi thấy ô này" lặng lẽ biến thành "chúng tôi biết cả bảng".

Bảng miếu vượng có 14 × 12 = 168 ô. Một lá số cho **14** ô. Con số ấy không đủ để
dựng bảng — nhưng đủ để **bác bỏ** một bảng đã chép, và đó chính là việc của module
này.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from cosmic_astrology.calendar.sexagenary import CHI
from cosmic_astrology.chart.types import StarStrength
from cosmic_astrology.stars.strength import StarStrengthTable

__all__ = [
    "CANONICAL_REFERENCES",
    "OBSERVED_STRENGTH_CELLS",
    "ReferenceChart",
    "StrengthMismatch",
    "validate_strength_table",
]

_PATH = Path(__file__).parent / "data" / "canonical_reference_charts.json"


@dataclass(frozen=True, slots=True)
class ReferenceChart:
    """Một lá số chuẩn và những ô đọc được từ nó."""

    id: str
    label: str
    note: str
    #: ``{mã sao: địa chi}`` — vị trí đọc trực tiếp từ lá số in.
    star_placements: Mapping[str, str]
    #: ``{(mã sao, địa chi): độ sáng}`` cho **14 chính tinh**. Khoá là **cặp**, không
    #: phải riêng mã sao: một ô của bảng là một cặp, và đánh khoá bằng mã sao sẽ ngầm
    #: nói "sao này độ sáng thế" ở mọi địa chi — đúng cái suy rộng bị cấm.
    strength_cells: Mapping[tuple[str, str], StarStrength]
    #: Như trên, nhưng cho sao **ngoài** 14 chính tinh. Để riêng vì bảng 14 × 12 là
    #: một khái niệm có biên rõ ràng, và trộn phụ tinh vào sẽ làm mọi phép đếm phủ
    #: sóng của bảng ấy vô nghĩa.
    non_major_strength_cells: Mapping[tuple[str, str], StarStrength]


@dataclass(frozen=True, slots=True)
class StrengthMismatch:
    """Một ô bảng không khớp lá số đối chiếu."""

    star_id: str
    branch: str
    expected: StarStrength
    actual: StarStrength | None

    def describe(self) -> str:
        got = self.actual.value if self.actual else "trống"
        return (
            f"{self.star_id} tại {self.branch}: bảng ghi {got}, "
            f"lá số đối chiếu ghi {self.expected.value}"
        )


def _parse_cells(raw: object, chart_id: str, field: str) -> Mapping[tuple[str, str], StarStrength]:
    valid_branches = set(CHI)
    valid_states = {s.value for s in StarStrength}
    cells: dict[tuple[str, str], StarStrength] = {}
    for cell in raw if isinstance(raw, list) else []:
        branch, state = cell["branch"], cell["strength"]
        if branch not in valid_branches:
            raise ValueError(f"{chart_id}/{field}: '{branch}' không phải địa chi")
        if state not in valid_states:
            raise ValueError(f"{chart_id}/{field}: '{state}' không phải độ sáng hợp lệ")
        key = (cell["star_id"], branch)
        if key in cells:
            raise ValueError(f"{chart_id}/{field}: ghi hai lần ô {key}")
        cells[key] = StarStrength(state)
    return MappingProxyType(cells)


def _load() -> tuple[ReferenceChart, ...]:
    raw = json.loads(_PATH.read_text(encoding="utf-8"))
    charts: list[ReferenceChart] = []

    for entry in raw["references"]:
        charts.append(
            ReferenceChart(
                id=entry["id"],
                label=entry["label"],
                note=entry.get("note", ""),
                star_placements=MappingProxyType(dict(entry.get("star_placements", {}))),
                strength_cells=_parse_cells(
                    entry.get("major_star_strength"), entry["id"], "major_star_strength"
                ),
                non_major_strength_cells=_parse_cells(
                    entry.get("non_major_star_strength"), entry["id"], "non_major_star_strength"
                ),
            )
        )
    return tuple(charts)


CANONICAL_REFERENCES: tuple[ReferenceChart, ...] = _load()


def validate_strength_table(
    table: StarStrengthTable,
    references: Sequence[ReferenceChart] = CANONICAL_REFERENCES,
) -> tuple[StrengthMismatch, ...]:
    """Đối chiếu một bảng miếu vượng với mọi ô đã quan sát được.

    Trả về danh sách ô lệch; rỗng nghĩa là bảng **chưa bị bác bỏ** — không phải là
    bảng đúng. Phân biệt ấy quan trọng: 14 ô khớp không nói gì về 154 ô còn lại.

    Bảng rỗng cũng trả về rỗng. Một bảng chưa điền thì không mâu thuẫn với gì cả, và
    bắt nó "trượt" sẽ biến bài kiểm này thành thứ phải tắt đi trong lúc chờ dữ liệu.
    """
    if table.is_empty:
        return ()
    mismatches: list[StrengthMismatch] = []
    for reference in references:
        for (star_id, branch), expected in reference.strength_cells.items():
            # Sao chưa vào bảng thì bỏ qua: bảng điền dần từng sao là hợp lệ, và
            # ``load_table`` đã canh riêng chuyện điền nửa vời trong một hàng.
            if star_id not in table.entries:
                continue
            actual = table.strength_for(star_id, branch)
            if actual is not expected:
                mismatches.append(StrengthMismatch(star_id, branch, expected, actual))
    return tuple(mismatches)


def _collect_observed() -> Mapping[tuple[str, str], StarStrength]:
    """Mọi ô ``(sao, địa chi)`` đọc được, gộp từ tất cả lá số đối chiếu.

    Gộp được vì **một ô độ sáng không phụ thuộc lá số**: "Tử Vi tại Dần là Miếu" đúng
    ở mọi lá số có Tử Vi ở Dần. Đó là lý do những ô này dùng được như dữ liệu thật
    chứ không chỉ như bài kiểm — chúng là *một phần bảng đã quan sát được*, không phải
    một suy đoán.

    Hai lá số đối chiếu ghi khác nhau ở cùng một ô là mâu thuẫn thật, và nó nổ ở đây
    thay vì im lặng để một trong hai giá trị thắng.
    """
    merged: dict[tuple[str, str], StarStrength] = {}
    for reference in CANONICAL_REFERENCES:
        for cells in (reference.strength_cells, reference.non_major_strength_cells):
            for key, value in cells.items():
                existing = merged.get(key)
                if existing is not None and existing is not value:
                    raise ValueError(
                        f"Hai lá số đối chiếu ghi khác nhau ở ô {key}: "
                        f"{existing.value} và {value.value}"
                    )
                merged[key] = value
    return MappingProxyType(merged)


#: Những ô bảng độ sáng **đã quan sát được**. Không phải bảng — bảng đầy đủ có 168 ô
#: cho riêng 14 chính tinh, và đây chỉ là những ô có người đọc ra từ một lá số in.
OBSERVED_STRENGTH_CELLS: Mapping[tuple[str, str], StarStrength] = _collect_observed()
