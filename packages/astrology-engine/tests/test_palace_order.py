"""Thứ tự 12 cung — bất biến nền tảng.

Kỳ vọng suy từ định nghĩa: từ cung Mệnh, đi **nghịch** chiều địa chi lần lượt là
Mệnh → Huynh Đệ → Phu Thê → Tử Tức → Tài Bạch → Tật Ách → Thiên Di → Nô Bộc →
Quan Lộc → Điền Trạch → Phúc Đức → Phụ Mẫu. Không giá trị nào ở đây lấy từ engine.

Engine 0.1.0 đi sai chiều, làm 10/12 nhãn cung lật gương quanh trục Mệnh–Thiên Di
mà vẫn giữ Mệnh và Thiên Di đúng chỗ, nên lỗi rất dễ lọt. Bộ test này chặn cả hai
đầu: đúng bảng, và không được trùng mẫu lật gương.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from cosmic_astrology import BirthInput, build_chart
from cosmic_astrology.calendar.sexagenary import CHI
from cosmic_astrology.chart.types import CalendarType, EngineStage, Gender, PalaceName

FIXTURE = Path(__file__).parent / "fixtures" / "palace_order.json"
GOLDEN: dict[str, Any] = json.loads(FIXTURE.read_text(encoding="utf-8"))
SEQUENCE: list[str] = GOLDEN["sequence"]

#: Một ca cho mỗi vị trí Mệnh. Cùng ngày, chỉ đổi giờ sinh, nên bảng dễ đọc lại.
BIRTH_BY_MENH: dict[str, int] = {
    "Tý": 2, "Sửu": 0, "Dần": 22, "Mão": 20, "Thìn": 18, "Tỵ": 16,
    "Ngọ": 14, "Mùi": 12, "Thân": 10, "Dậu": 8, "Tuất": 6, "Hợi": 4,
}  # fmt: skip


def _mapping(chart: dict[str, Any]) -> dict[str, str]:
    return {p["branch"]: p["name"] for p in chart["palaces"]}


def _expected_for(menh_branch: str) -> dict[str, str]:
    """Bảng kỳ vọng, suy từ định nghĩa cho một vị trí Mệnh bất kỳ."""
    menh = CHI.index(menh_branch)
    return {CHI[(menh - offset) % 12]: name for offset, name in enumerate(SEQUENCE)}


def _mirrored_for(menh_branch: str) -> dict[str, str]:
    menh = CHI.index(menh_branch)
    return {CHI[(menh + offset) % 12]: name for offset, name in enumerate(SEQUENCE)}


def _build(hour: int) -> dict[str, Any]:
    return build_chart(
        BirthInput(
            name="palace-order",
            gender=Gender.MALE,
            calendar_type=CalendarType.SOLAR,
            day=5,
            month=1,
            year=1985,
            hour=hour,
            timezone_id="Asia/Ho_Chi_Minh",
        ),
        stage=EngineStage.PREVIEW,
    ).to_dict()


def test_the_golden_fixture_describes_a_complete_and_consistent_rule() -> None:
    """Fixture phải tự đứng vững: đủ 12 cung, 12 địa chi, và khớp định nghĩa."""
    assert sorted(GOLDEN["expected"]) == sorted(GOLDEN["branches"])
    assert sorted(GOLDEN["expected"].values()) == sorted(p.value for p in PalaceName)
    assert GOLDEN["expected"] == _expected_for(GOLDEN["menh_branch"])


def test_golden_case_menh_tuat_matches_the_fixture_exactly() -> None:
    birth = GOLDEN["birth"]
    chart = build_chart(
        BirthInput(
            name=GOLDEN["id"],
            gender=Gender(birth["gender"]),
            calendar_type=CalendarType(birth["calendar"]),
            day=birth["day"],
            month=birth["month"],
            year=birth["year"],
            hour=birth["hour"],
            minute=birth["minute"],
            timezone_id=birth["timezone_id"],
        ),
        stage=EngineStage.PREVIEW,
    ).to_dict()

    assert chart["menh"]["branch"] == GOLDEN["menh_branch"]
    assert _mapping(chart) == GOLDEN["expected"]


def test_golden_case_does_not_match_the_mirrored_pattern() -> None:
    """Lật gương giữ Mệnh và Thiên Di đúng chỗ, nên phải đối chiếu cả bảng."""
    mirrored = {k: v for k, v in GOLDEN["wrong_mirrored_pattern"].items() if k != "_README"}
    assert mirrored == _mirrored_for(GOLDEN["menh_branch"])
    assert mirrored != GOLDEN["expected"]


@pytest.mark.parametrize(("menh_branch", "hour"), sorted(BIRTH_BY_MENH.items()))
def test_palace_order_holds_for_every_menh_position(menh_branch: str, hour: int) -> None:
    chart = _build(hour)
    assert chart["menh"]["branch"] == menh_branch, "ca mẫu không còn cho Mệnh như bảng"
    assert _mapping(chart) == _expected_for(menh_branch)
    assert _mapping(chart) != _mirrored_for(menh_branch)


@pytest.mark.parametrize(("menh_branch", "hour"), sorted(BIRTH_BY_MENH.items()))
def test_thien_di_is_always_opposite_menh(menh_branch: str, hour: int) -> None:
    chart = _build(hour)
    by_name = {p["name"]: p["branch_index"] for p in chart["palaces"]}
    assert (by_name["THIEN_DI"] - by_name["MENH"]) % 12 == 6


@pytest.mark.parametrize(("menh_branch", "hour"), sorted(BIRTH_BY_MENH.items()))
def test_every_palace_name_appears_exactly_once(menh_branch: str, hour: int) -> None:
    names = [p["name"] for p in _build(hour)["palaces"]]
    assert sorted(names) == sorted(p.value for p in PalaceName)


def test_stars_stay_on_their_branch_regardless_of_palace_names() -> None:
    """Tên cung là nhãn; sao gắn vào địa chi.

    Hai lá số khác giờ sinh có Mệnh khác nhau, nên nhãn cung khác nhau. Nhưng nếu
    ngày âm và Cục trùng nhau thì các sao vẫn phải nằm ở đúng những địa chi ấy —
    sửa nhãn cung không bao giờ được kéo sao đi theo.
    """

    def stars_by_branch(chart: dict[str, Any]) -> dict[str, str]:
        return {s["id"]: p["branch"] for p in chart["palaces"] for s in p["major_stars"]}

    a, b = _build(6), _build(8)
    assert a["menh"]["branch"] != b["menh"]["branch"]
    assert _mapping(a) != _mapping(b)
    same_cuc = a["cuc"]["number"] == b["cuc"]["number"]
    same_lunar_day = a["lunar_birth"]["day"] == b["lunar_birth"]["day"]
    if same_cuc and same_lunar_day:
        assert stars_by_branch(a) == stars_by_branch(b)
