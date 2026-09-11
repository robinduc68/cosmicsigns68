"""Review states, promotion, and the safeguards against self-confirmation.

The thing being defended here is simple: a fixture must not be able to claim
VERIFIED on the strength of the engine's own output.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from cosmic_astrology.conventions import COSMIC_SIGNS_STANDARD_V1, RuleId
from cosmic_astrology.review import (
    ComparisonStatus,
    Discrepancy,
    DiscrepancyStatus,
    FixtureReview,
    ReviewState,
    Source,
    SourceType,
    compare_stars,
    evaluate_state,
    load_store,
    promote_rule_verification,
)
from cosmic_astrology.review.store import MATRIX_PATH, SOURCES_PATH

PRIMARY = Source(
    id="primary-book",
    title="Tử Vi Đẩu Số (ấn bản thử nghiệm)",
    source_type=SourceType.PRIMARY_SELECTED_REFERENCE,
    publication_year=1990,
    school="Nam phái",
)
CROSS_CHECK = Source(
    id="cross-check",
    title="Nguồn đối chiếu phụ",
    source_type=SourceType.CROSS_CHECK_REFERENCE,
    publication_year=2001,
)


@pytest.fixture
def store(tmp_path: Path):  # type: ignore[no-untyped-def]
    """A throwaway copy of the real matrix, so tests never edit the repo file."""
    matrix = tmp_path / "matrix.json"
    sources = tmp_path / "sources.json"
    shutil.copy(MATRIX_PATH, matrix)
    shutil.copy(SOURCES_PATH, sources)
    loaded = load_store(matrix, sources)
    loaded.add_source(PRIMARY)
    loaded.add_source(CROSS_CHECK)
    return loaded


def _candidate(store, fixture_id: str) -> dict[str, str]:  # type: ignore[no-untyped-def]
    candidate = store.record(fixture_id).candidate
    assert candidate is not None
    return dict(candidate)


def _full_review(**over: object) -> FixtureReview:
    base: dict[str, object] = {
        "reviewer": "Người thẩm định thử",
        "reviewed_at": "2026-09-11",
        "source_id": "primary-book",
        "independently_confirmed": True,
    }
    base.update(over)
    return FixtureReview(**base)  # type: ignore[arg-type]


# ------------------------------------------------------------------ comparison


def test_a_missing_expectation_is_unverified_not_a_match() -> None:
    rows = compare_stars({"TU_VI": "Mùi"}, None)
    assert all(r.status is ComparisonStatus.UNVERIFIED for r in rows)


def test_mismatch_is_detected_per_star() -> None:
    rows = compare_stars({"TU_VI": "Mùi", "THIEN_CO": "Ngọ"}, {"TU_VI": "Mùi", "THIEN_CO": "Dần"})
    by_star = {r.star: r.status for r in rows}
    assert by_star["TU_VI"] is ComparisonStatus.MATCH
    assert by_star["THIEN_CO"] is ComparisonStatus.MISMATCH


# ----------------------------------------------------------------- state rules


def test_a_fresh_fixture_is_pending(store) -> None:  # type: ignore[no-untyped-def]
    assert store.record("TV-S1").evaluate(store.registry).state is ReviewState.PENDING


def test_the_late_zi_fixture_is_blocked_not_pending(store) -> None:  # type: ignore[no-untyped-def]
    evaluation = store.record("TV-B1").evaluate(store.registry)
    assert evaluation.state is ReviewState.BLOCKED
    assert evaluation.blockers


def test_partial_entry_is_in_review(store) -> None:  # type: ignore[no-untyped-def]
    evaluation = store.save_review("TV-S1", FixtureReview(reviewer="Ai đó"))
    assert evaluation.state is ReviewState.IN_REVIEW


def test_a_mismatch_becomes_disagreement_and_engine_is_untouched(store) -> None:  # type: ignore[no-untyped-def]
    candidate = _candidate(store, "TV-S1")
    wrong = dict(candidate)
    wrong["THIEN_CO"] = "Tý" if candidate["THIEN_CO"] != "Tý" else "Sửu"

    evaluation = store.save_review(
        "TV-S1", _full_review(expected_tu_vi=candidate["TU_VI"], expected_stars=wrong)
    )
    assert evaluation.state is ReviewState.DISAGREEMENT
    assert "THIEN_CO" in evaluation.mismatches
    # The candidate block must survive a disagreement untouched.
    assert _candidate(store, "TV-S1") == candidate


def test_full_agreement_plus_evidence_is_verified(store) -> None:  # type: ignore[no-untyped-def]
    candidate = _candidate(store, "TV-S1")
    evaluation = store.save_review(
        "TV-S1", _full_review(expected_tu_vi=candidate["TU_VI"], expected_stars=candidate)
    )
    assert evaluation.state is ReviewState.VERIFIED


# --------------------------------------------------------- anti-copy safeguard


def test_agreement_without_the_confirmation_flag_is_not_verified(store) -> None:  # type: ignore[no-untyped-def]
    """Identical values are exactly when a copied review is invisible."""
    candidate = _candidate(store, "TV-S1")
    evaluation = store.save_review(
        "TV-S1",
        _full_review(
            expected_tu_vi=candidate["TU_VI"],
            expected_stars=candidate,
            independently_confirmed=False,
        ),
    )
    assert evaluation.state is ReviewState.IN_REVIEW
    assert any("independently_confirmed" in b for b in evaluation.blockers)


@pytest.mark.parametrize("missing", ["reviewer", "reviewed_at", "source_id"])
def test_agreement_without_full_provenance_is_not_verified(store, missing: str) -> None:  # type: ignore[no-untyped-def]
    candidate = _candidate(store, "TV-S1")
    evaluation = store.save_review(
        "TV-S1",
        _full_review(
            expected_tu_vi=candidate["TU_VI"], expected_stars=candidate, **{missing: None}
        ),
    )
    assert evaluation.state is not ReviewState.VERIFIED


def test_a_source_too_vague_to_re_check_does_not_count(store) -> None:  # type: ignore[no-untyped-def]
    store.add_source(
        Source(id="vague", title="Một quyển sách", source_type=SourceType.SECONDARY_REFERENCE)
    )
    candidate = _candidate(store, "TV-S1")
    evaluation = store.save_review(
        "TV-S1",
        _full_review(
            expected_tu_vi=candidate["TU_VI"], expected_stars=candidate, source_id="vague"
        ),
    )
    assert evaluation.state is ReviewState.IN_REVIEW
    assert any("tra lại" in b for b in evaluation.blockers)


def test_a_stored_state_field_is_never_trusted(store) -> None:  # type: ignore[no-untyped-def]
    """Hand-editing the file to say VERIFIED must not make it so."""
    data = json.loads(store.matrix_path.read_text(encoding="utf-8"))
    for case in data["cases"]:
        if case["id"] == "TV-S1":
            case["review"]["state"] = "VERIFIED"
    store.matrix_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    reloaded = load_store(store.matrix_path, store.sources_path)
    assert reloaded.record("TV-S1").evaluate(reloaded.registry).state is ReviewState.PENDING


def test_an_incomplete_star_set_cannot_be_verified(store) -> None:  # type: ignore[no-untyped-def]
    candidate = _candidate(store, "TV-S1")
    partial = {k: v for k, v in list(candidate.items())[:10]}
    evaluation = store.save_review(
        "TV-S1", _full_review(expected_tu_vi=candidate["TU_VI"], expected_stars=partial)
    )
    assert evaluation.state is ReviewState.IN_REVIEW


# -------------------------------------------------------------------- promotion


def _verify_all(store) -> None:  # type: ignore[no-untyped-def]
    for record in store.records:
        if record.blocked_reason:
            continue
        candidate = _candidate(store, record.id)
        store.save_review(
            record.id, _full_review(expected_tu_vi=candidate["TU_VI"], expected_stars=candidate)
        )


def test_promotion_is_refused_while_fixtures_are_pending(store) -> None:  # type: ignore[no-untyped-def]
    result = promote_rule_verification(
        rule=RuleId.MAJOR_STARS,
        store=store,
        profile=COSMIC_SIGNS_STANDARD_V1,
        reviewer="Ai đó",
        source_id="primary-book",
        evidence="đã đối chiếu",
    )
    assert result.granted is False
    assert any("chưa thẩm định" in r for r in result.reasons)


def test_promotion_needs_reviewer_source_and_evidence(store) -> None:  # type: ignore[no-untyped-def]
    _verify_all(store)
    result = promote_rule_verification(
        rule=RuleId.MAJOR_STARS,
        store=store,
        profile=COSMIC_SIGNS_STANDARD_V1,
        reviewer=None,
        source_id=None,
        evidence="",
    )
    assert result.granted is False
    joined = " ".join(result.reasons)
    assert "người thẩm định" in joined and "nguồn" in joined and "bằng chứng" in joined


def test_a_cross_check_source_cannot_promote_a_rule(store) -> None:  # type: ignore[no-untyped-def]
    """Only the reference the convention points at carries that weight."""
    _verify_all(store)
    result = promote_rule_verification(
        rule=RuleId.MAJOR_STARS,
        store=store,
        profile=COSMIC_SIGNS_STANDARD_V1,
        reviewer="Ai đó",
        source_id="cross-check",
        evidence="đã đối chiếu 16 ca",
    )
    assert result.granted is False
    assert any("PRIMARY_SELECTED_REFERENCE" in r for r in result.reasons)


def test_an_open_discrepancy_blocks_promotion(store) -> None:  # type: ignore[no-untyped-def]
    _verify_all(store)
    store.add_discrepancy(
        Discrepancy(
            id="D001", fixture_id="TV-S1", rule_id="major_stars", subject="THIEN_CO",
            candidate="Ngọ", expected="Tý", source_id="primary-book", reviewer="Ai đó",
            recorded_at="2026-09-11", status=DiscrepancyStatus.OPEN,
        )
    )
    result = promote_rule_verification(
        rule=RuleId.MAJOR_STARS, store=store, profile=COSMIC_SIGNS_STANDARD_V1,
        reviewer="Ai đó", source_id="primary-book", evidence="đã đối chiếu 16 ca",
    )
    assert result.granted is False
    assert any("D001" in r for r in result.reasons)


def test_promotion_is_granted_only_with_everything_in_place(store) -> None:  # type: ignore[no-untyped-def]
    """The gate must be able to open, or it is teaching nothing."""
    _verify_all(store)
    result = promote_rule_verification(
        rule=RuleId.MAJOR_STARS, store=store, profile=COSMIC_SIGNS_STANDARD_V1,
        reviewer="Người thẩm định thử", source_id="primary-book",
        evidence="Đối chiếu 16 ca với ấn bản đã chọn, tr. 100–160.",
    )
    assert result.granted is True, result.reasons


def test_promotion_still_refuses_an_unresolved_rule(store) -> None:  # type: ignore[no-untyped-def]
    _verify_all(store)
    result = promote_rule_verification(
        rule=RuleId.STAR_STRENGTH, store=store, profile=COSMIC_SIGNS_STANDARD_V1,
        reviewer="Ai đó", source_id="primary-book", evidence="…",
    )
    assert result.granted is False
    assert any("UNRESOLVED" in r for r in result.reasons)


def test_promotion_never_mutates_the_profile(store) -> None:  # type: ignore[no-untyped-def]
    before = COSMIC_SIGNS_STANDARD_V1.binding(RuleId.MAJOR_STARS).verification
    _verify_all(store)
    promote_rule_verification(
        rule=RuleId.MAJOR_STARS, store=store, profile=COSMIC_SIGNS_STANDARD_V1,
        reviewer="Ai đó", source_id="primary-book", evidence="đủ",
    )
    assert COSMIC_SIGNS_STANDARD_V1.binding(RuleId.MAJOR_STARS).verification is before


def test_evaluate_state_needs_no_store(store) -> None:  # type: ignore[no-untyped-def]
    """The decision is pure, so it can be reasoned about in isolation."""
    evaluation = evaluate_state(
        review=FixtureReview(), candidate={"TU_VI": "Mùi"}, source=None, blocked_reason=None
    )
    assert evaluation.state is ReviewState.PENDING
