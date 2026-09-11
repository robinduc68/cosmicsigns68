"""Guards around the major-star verification matrix.

These tests deliberately do **not** assert star positions. The matrix exists to
be checked against an outside authority; asserting the engine against its own
output would only prove it is self-consistent. What is guarded here is the
*process*: the fixture stays well-formed, coverage does not silently shrink, and
nobody can promote a case to "verified" without the evidence to back it.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from cosmic_astrology import BirthInput, build_chart
from cosmic_astrology.chart.types import CalendarType, EngineStage, Gender
from cosmic_astrology.conventions import COSMIC_SIGNS_STANDARD_V1
from cosmic_astrology.review import ReviewState, ReviewStore, load_store

FIXTURE = Path(__file__).parent / "fixtures" / "major_stars_matrix.json"

MAJOR_STAR_CODES = {
    "TU_VI", "THIEN_CO", "THAI_DUONG", "VU_KHUC", "THIEN_DONG", "LIEM_TRINH",
    "THIEN_PHU", "THAI_AM", "THAM_LANG", "CU_MON", "THIEN_TUONG", "THIEN_LUONG",
    "THAT_SAT", "PHA_QUAN",
}  # fmt: skip

REVIEW_KEYS = {
    "state", "expected_tu_vi", "expected_stars", "expected_tuan", "expected_triet",
    "independently_confirmed", "reviewer", "reviewed_at", "source_id", "page", "notes",
}  # fmt: skip


def _matrix() -> dict[str, Any]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _cases() -> list[dict[str, Any]]:
    return _matrix()["cases"]


def _placeable() -> list[dict[str, Any]]:
    """Cases the default profile can actually build (TV-B1 is blocked on Q6)."""
    return [c for c in _cases() if "blocked" not in c]


@pytest.fixture(scope="module")
def store() -> ReviewStore:
    return load_store()


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
        timezone_id=i.get("timezone_id"),
    )
    return build_chart(birth, stage=EngineStage.PREVIEW).to_dict()


def test_every_case_has_a_unique_birth_input() -> None:
    seen = {json.dumps(c["input"], sort_keys=True) for c in _cases()}
    assert len(seen) == len(_cases()), "có ca trùng input — không thêm được độ phủ nào"


@pytest.mark.parametrize("case", _cases(), ids=lambda c: c["id"])
def test_every_case_keeps_reviewer_findings_in_their_own_block(case: dict[str, Any]) -> None:
    """Engine output and reviewer findings live apart; the old flat fields are gone."""
    assert set(case["review"]) == REVIEW_KEYS
    for legacy in ("expected_stars", "expected_tu_vi", "verified_against_source", "reviewer"):
        assert legacy not in case, f"{case['id']}: còn trường cũ '{legacy}' ngoài khối review"


def test_matrix_covers_every_cuc_and_the_four_yin_yang_combinations() -> None:
    frames = [c["derived_frame"] for c in _placeable()]
    assert {f["cuc_number"] for f in frames} == {2, 3, 4, 5, 6}
    assert {f["yin_yang"] for f in frames} == {"Dương Nam", "Âm Nam", "Dương Nữ", "Âm Nữ"}
    # Đủ rộng để một lỗi an sao không thể lọt qua vì mọi ca đều giống nhau.
    assert len({f["menh"] for f in frames}) >= 8, "cần nhiều vị trí Mệnh khác nhau"


def test_matrix_covers_the_tu_vi_thien_phu_conjunction_at_both_axes() -> None:
    # Tử Vi và Thiên Phủ chỉ trùng cung tại Dần hoặc Thân — cả hai phải có ca.
    conjunctions = {
        c["engine_candidate_stars"]["TU_VI"]
        for c in _placeable()
        if c["engine_candidate_stars"]["TU_VI"] == c["engine_candidate_stars"]["THIEN_PHU"]
    }
    assert conjunctions == {"Dần", "Thân"}


@pytest.mark.parametrize("case", _placeable(), ids=lambda c: c["id"])
def test_engine_still_produces_the_recorded_candidate(case: dict[str, Any]) -> None:
    """The fixture must not drift from the engine without someone noticing."""
    chart = _build(case)
    actual = {s["id"]: p["branch"] for p in chart["palaces"] for s in p["major_stars"]}
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
        p["branch"] for p in chart["palaces"] for s in p["major_stars"] if s["id"] == "TU_VI"
    )
    assert chart["lunar_birth"]["day"] == 1
    assert tu_vi == case["anchor_tu_vi"]


@pytest.mark.parametrize("case", _cases(), ids=lambda c: c["id"])
def test_a_verified_state_is_always_backed_by_evidence(
    case: dict[str, Any], store: ReviewStore
) -> None:
    """A stored label can never claim more than the evidence in the file supports."""
    record = store.record(case["id"])
    evaluation = record.evaluate(store.registry)

    if case["review"]["state"] == ReviewState.VERIFIED.value:
        assert evaluation.state is ReviewState.VERIFIED, (
            f"{case['id']}: ghi VERIFIED nhưng bằng chứng không đủ: {evaluation.blockers}"
        )
    if evaluation.state is ReviewState.VERIFIED:
        review = record.review
        assert review.has_expected_values
        assert review.reviewer and review.reviewed_at and review.source_id
        assert review.independently_confirmed


@pytest.mark.parametrize("case", _cases(), ids=lambda c: c["id"])
def test_expected_values_are_never_copied_from_engine_output(case: dict[str, Any]) -> None:
    """The whole point of the matrix: truth has to come from outside the engine.

    An ``expected_stars`` block byte-identical to the candidate, without an explicit
    independent confirmation, is the signature of somebody pasting the engine's
    answer in — which would make the fixture prove nothing.
    """
    review = case["review"]
    expected = review.get("expected_stars")
    if expected is None:
        return
    candidate = case.get("engine_candidate_stars")
    copied = candidate is not None and expected == candidate
    if copied and not review.get("independently_confirmed"):
        pytest.fail(
            f"{case['id']}: expected_stars trùng khít engine_candidate_stars. Nếu nguồn "
            "thật sự cho kết quả y hệt, tích independently_confirmed kèm reviewer."
        )


@pytest.mark.parametrize("case", _cases(), ids=lambda c: c["id"])
def test_every_case_records_the_convention_it_belongs_to(case: dict[str, Any]) -> None:
    """A star position without a convention is not a fact about anything."""
    assert case["convention_profile"] == COSMIC_SIGNS_STANDARD_V1.profile_id
    assert case["convention_version"] == COSMIC_SIGNS_STANDARD_V1.version


def test_the_blocked_case_demonstrates_all_three_late_zi_policies() -> None:
    blocked = [c for c in _cases() if "blocked" in c]
    assert len(blocked) == 1, "TV-B1 là ca chứng minh cho Q6"
    demo = blocked[0]["late_zi_demonstration"]
    assert set(demo) == {"CIVIL_DAY", "LATE_ZI_NEXT_DAY", "PILLAR_ONLY_NEXT_DAY"}
    # Ba chính sách phải cho ba kết quả khác nhau, nếu không thì Q6 đâu có gì để chọn.
    assert len({(d["lunar_day"], d["day_pillar"], d["tu_vi"]) for d in demo.values()}) == 3


def test_source_of_truth_is_still_open_so_stars_stay_provisional(store: ReviewStore) -> None:
    """Chưa thẩm định xong thì mọi sao phải còn mang cờ provisional.

    Ngày nào mọi ca đều VERIFIED, test này sẽ đỏ — đó là tín hiệu đúng lúc để xem
    lại điều kiện gỡ cờ, chứ không phải lỗi.
    """
    verified = [fid for fid, ev in store.states().items() if ev.state is ReviewState.VERIFIED]
    if len(verified) == len(_placeable()):
        pytest.fail("Mọi ca đã thẩm định — xem lại điều kiện lên stage FULL (docs mục 3)")

    chart = _build(_placeable()[0])
    stars = [s for p in chart["palaces"] for s in p["major_stars"]]
    assert stars and all(s["provisional"] for s in stars)


def test_blocked_cases_say_why() -> None:
    for case in _cases():
        if "blocked" in case:
            assert len(case["blocked"]) > 40, f"{case['id']}: lý do chặn phải nói rõ"
