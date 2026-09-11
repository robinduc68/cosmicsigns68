"""Guards around the major-star verification matrix.

These tests deliberately do **not** assert star positions. The matrix exists to
be checked against an outside authority; asserting the engine against its own
output would only prove it is self-consistent. What is guarded here is the
*process*: the fixture stays well-formed, coverage does not silently shrink, and
nobody can promote a case to "verified" without supplying expected values.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from cosmic_astrology import BirthInput, build_chart
from cosmic_astrology.chart.types import CalendarType, EngineStage, Gender

FIXTURE = Path(__file__).parent / "fixtures" / "major_stars_matrix.json"

MAJOR_STAR_CODES = {
    "TU_VI", "THIEN_CO", "THAI_DUONG", "VU_KHUC", "THIEN_DONG", "LIEM_TRINH",
    "THIEN_PHU", "THAI_AM", "THAM_LANG", "CU_MON", "THIEN_TUONG", "THIEN_LUONG",
    "THAT_SAT", "PHA_QUAN",
}  # fmt: skip


def _matrix() -> dict[str, Any]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _cases() -> list[dict[str, Any]]:
    return _matrix()["cases"]


def _build(case: dict[str, Any]) -> dict[str, Any]:
    i = case["input"]
    birth = BirthInput(
        name=case["id"],
        gender=Gender(i["gender"]),
        calendar_type=CalendarType(i["calendar"]),
        day=i["day"],
        month=i["month"],
        year=i["year"],
        hour=i["hour"],
        minute=i["minute"],
        is_leap_month=i["is_leap_month"],
        tz_offset=i["tz_offset"],
        birth_place=None,
    )
    return build_chart(birth, stage=EngineStage.PREVIEW).to_dict()


def test_every_case_has_a_unique_birth_input() -> None:
    seen = {json.dumps(c["input"], sort_keys=True) for c in _cases()}
    assert len(seen) == len(_cases()), "có ca trùng input — không thêm được độ phủ nào"


def test_matrix_covers_every_cuc_and_the_four_yin_yang_combinations() -> None:
    frames = [c["derived_frame"] for c in _cases()]
    assert {f["cuc_number"] for f in frames} == {2, 3, 4, 5, 6}
    assert {f["yin_yang"] for f in frames} == {"Dương Nam", "Âm Nam", "Dương Nữ", "Âm Nữ"}
    # Đủ rộng để một lỗi an sao không thể lọt qua vì mọi ca đều giống nhau.
    assert len({f["menh"] for f in frames}) >= 8, "cần nhiều vị trí Mệnh khác nhau"


def test_matrix_covers_the_tu_vi_thien_phu_conjunction_at_both_axes() -> None:
    # Tử Vi và Thiên Phủ chỉ trùng cung tại Dần hoặc Thân — cả hai phải có ca.
    conjunctions = {
        c["engine_candidate_stars"]["TU_VI"]
        for c in _cases()
        if c["engine_candidate_stars"]["TU_VI"] == c["engine_candidate_stars"]["THIEN_PHU"]
    }
    assert conjunctions == {"Dần", "Thân"}


@pytest.mark.parametrize("case", _cases(), ids=lambda c: c["id"])
def test_engine_still_produces_the_recorded_candidate(case: dict[str, Any]) -> None:
    """The fixture must not drift from the engine without someone noticing."""
    chart = _build(case)
    actual = {s["code"]: p["branch"] for p in chart["palaces"] for s in p["major_stars"]}
    assert actual.keys() == MAJOR_STAR_CODES
    assert actual == case["engine_candidate_stars"], (
        f"{case['id']}: engine đã đổi kết quả. Nếu là sửa có chủ đích thì cập nhật "
        "fixture VÀ thẩm định lại ca này."
    )


@pytest.mark.parametrize(
    "case", [c for c in _cases() if "anchor_tu_vi" in c], ids=lambda c: c["id"]
)
def test_day_one_anchors_match_the_classical_table(case: dict[str, Any]) -> None:
    """Mùng 1: Thủy nhị→Sửu, Mộc tam→Thìn, Kim tứ→Hợi, Thổ ngũ→Ngọ, Hỏa lục→Dậu.

    Mốc kinh điển được nhiều nguồn đồng thuận, nên dùng làm lưới an toàn. Vẫn phải
    xác nhận lại theo nguồn đã chốt (Q1/Q2) trước khi engine lên stage FULL.
    """
    chart = _build(case)
    tu_vi = next(
        p["branch"] for p in chart["palaces"] for s in p["major_stars"] if s["code"] == "TU_VI"
    )
    assert chart["lunar_birth"]["day"] == 1
    assert tu_vi == case["anchor_tu_vi"]


@pytest.mark.parametrize("case", _cases(), ids=lambda c: c["id"])
def test_a_case_is_only_verified_once_expected_values_exist(case: dict[str, Any]) -> None:
    """Không ai được đánh dấu 'đã thẩm định' mà bỏ trống giá trị kỳ vọng."""
    if case["verified_against_source"]:
        assert case["expected_stars"], f"{case['id']}: verified nhưng expected_stars trống"
        assert case["expected_stars"].keys() == MAJOR_STAR_CODES


def test_source_of_truth_is_still_open_so_stars_stay_provisional() -> None:
    """Chưa chốt nguồn thì mọi sao phải còn mang cờ provisional.

    Ngày nào chốt được nguồn và thẩm định xong, test này sẽ đỏ — đó là tín hiệu
    đúng lúc để gỡ cờ, chứ không phải lỗi.
    """
    matrix = _matrix()
    unverified = [c["id"] for c in matrix["cases"] if not c["verified_against_source"]]
    if not unverified:
        pytest.fail("Mọi ca đã thẩm định — xem lại điều kiện lên stage FULL (docs mục 3)")

    chart = _build(matrix["cases"][0])
    stars = [s for p in chart["palaces"] for s in p["major_stars"]]
    assert stars and all(s["provisional"] for s in stars)


def test_blocked_cases_say_why() -> None:
    for case in _cases():
        if "blocked" in case:
            assert len(case["blocked"]) > 40, f"{case['id']}: lý do chặn phải nói rõ"
