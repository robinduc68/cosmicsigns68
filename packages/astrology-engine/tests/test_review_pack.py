"""Export and import of the reviewer pack.

The pack leaves the building with blank expectations and must come back with
answers a person wrote. Both halves of that sentence are enforced here.
"""

from __future__ import annotations

import csv
import io
import shutil
from pathlib import Path

import pytest

from cosmic_astrology.review import (
    ReviewState,
    Source,
    SourceType,
    apply_import,
    export_csv,
    export_json,
    load_store,
    preview_import,
)
from cosmic_astrology.review.model import MAJOR_STAR_CODES
from cosmic_astrology.review.store import MATRIX_PATH, SOURCES_PATH


@pytest.fixture
def store(tmp_path: Path):  # type: ignore[no-untyped-def]
    matrix = tmp_path / "matrix.json"
    sources = tmp_path / "sources.json"
    shutil.copy(MATRIX_PATH, matrix)
    shutil.copy(SOURCES_PATH, sources)
    loaded = load_store(matrix, sources)
    loaded.add_source(
        Source(
            id="primary-book",
            title="Ấn bản thử nghiệm",
            source_type=SourceType.PRIMARY_SELECTED_REFERENCE,
            publication_year=1990,
        )
    )
    return loaded


def _rows(csv_text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(csv_text)))


# ----------------------------------------------------------------------- export


def test_the_pack_covers_every_fixture(store) -> None:  # type: ignore[no-untyped-def]
    rows = _rows(export_csv(store))
    assert len(rows) == len(store.records)
    assert {r["fixture_id"] for r in rows} == {r.id for r in store.records}


def test_expected_columns_ship_empty(store) -> None:  # type: ignore[no-untyped-def]
    """A pre-filled guess would make the review a rubber stamp."""
    for row in _rows(export_csv(store)):
        assert row["expected_tu_vi"] == ""
        for code in MAJOR_STAR_CODES:
            assert row[f"expected_{code}"] == ""


def test_the_pack_carries_the_engine_candidate_for_comparison(store) -> None:  # type: ignore[no-untyped-def]
    row = next(r for r in _rows(export_csv(store)) if r["fixture_id"] == "TV-S1")
    assert row["engine_TU_VI"]
    assert row["birth_date"] == "10/09/1992"
    assert row["lunar_date"].startswith("14/8")


def test_a_blocked_fixture_says_so_instead_of_carrying_stars(store) -> None:  # type: ignore[no-untyped-def]
    row = next(r for r in _rows(export_csv(store)) if r["fixture_id"] == "TV-B1")
    assert row["lunar_date"] == "(bị chặn)"
    assert row["engine_TU_VI"] == ""


def test_the_json_pack_warns_against_copying(store) -> None:  # type: ignore[no-untyped-def]
    payload = export_json(store)
    assert "Đừng chép" in payload
    assert "expected_tu_vi" in payload


# ----------------------------------------------------------------------- import


def _filled_row(store, fixture_id: str, **over: str) -> dict[str, str]:  # type: ignore[no-untyped-def]
    candidate = store.record(fixture_id).candidate or {}
    row = {
        "fixture_id": fixture_id,
        "expected_tu_vi": candidate.get("TU_VI", ""),
        "reviewer": "Người thẩm định thử",
        "reviewed_at": "2026-09-11",
        "source_id": "primary-book",
        "page": "tr. 120",
        "independently_confirmed": "true",
        "notes": "",
        "expected_tuan": "",
        "expected_triet": "",
    }
    for code in MAJOR_STAR_CODES:
        row[f"expected_{code}"] = candidate.get(code, "")
    row.update(over)
    return row


def _to_csv(rows: list[dict[str, str]]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def test_a_blank_pack_changes_nothing(store) -> None:  # type: ignore[no-untyped-def]
    outcome = preview_import(store, export_csv(store))
    assert not outcome.accepted
    assert len(outcome.skipped) == len(store.records)
    assert outcome.is_clean


def test_import_is_preview_only_until_applied(store) -> None:  # type: ignore[no-untyped-def]
    outcome = preview_import(store, _to_csv([_filled_row(store, "TV-S1")]))
    assert "TV-S1" in outcome.accepted
    # Nothing written yet.
    assert store.record("TV-S1").evaluate(store.registry).state is ReviewState.PENDING

    applied = apply_import(store, outcome)
    assert applied["TV-S1"] == ReviewState.VERIFIED.value


def test_import_never_touches_the_candidate_block(store) -> None:  # type: ignore[no-untyped-def]
    before = dict(store.record("TV-S1").candidate or {})
    apply_import(store, preview_import(store, _to_csv([_filled_row(store, "TV-S1")])))
    assert store.record("TV-S1").candidate == before


def test_a_half_filled_row_is_rejected(store) -> None:  # type: ignore[no-untyped-def]
    row = _filled_row(store, "TV-S1")
    row["expected_THAT_SAT"] = ""
    outcome = preview_import(store, _to_csv([row]))
    assert not outcome.accepted
    assert any("thiếu" in r for r in outcome.rejected)


@pytest.mark.parametrize(
    ("field", "message"), [("reviewer", "người thẩm định"), ("source_id", "source_id")]
)
def test_missing_provenance_is_rejected(store, field: str, message: str) -> None:  # type: ignore[no-untyped-def]
    outcome = preview_import(store, _to_csv([_filled_row(store, "TV-S1", **{field: ""})]))
    assert not outcome.accepted
    assert any(message in r for r in outcome.rejected)


def test_an_unknown_source_is_rejected(store) -> None:  # type: ignore[no-untyped-def]
    outcome = preview_import(store, _to_csv([_filled_row(store, "TV-S1", source_id="nope")]))
    assert any("sổ nguồn" in r for r in outcome.rejected)


def test_an_unknown_fixture_is_rejected(store) -> None:  # type: ignore[no-untyped-def]
    row = _filled_row(store, "TV-S1")
    row["fixture_id"] = "TV-ZZ"
    outcome = preview_import(store, _to_csv([row]))
    assert any("TV-ZZ" in r for r in outcome.rejected)


def test_a_file_of_the_wrong_shape_is_rejected(store) -> None:  # type: ignore[no-untyped-def]
    outcome = preview_import(store, "a,b,c\n1,2,3\n")
    assert not outcome.is_clean
    assert any("fixture_id" in r for r in outcome.rejected)


def test_a_pack_with_any_rejection_cannot_be_applied_partially(store) -> None:  # type: ignore[no-untyped-def]
    """Half-importing would leave the matrix reviewed with no record of which half."""
    rows = [_filled_row(store, "TV-S1"), _filled_row(store, "TV-S2", reviewer="")]
    outcome = preview_import(store, _to_csv(rows))
    assert not outcome.is_clean
    with pytest.raises(ValueError, match="không nhập một phần"):
        apply_import(store, outcome)
    assert store.record("TV-S1").evaluate(store.registry).state is ReviewState.PENDING


def test_an_imported_disagreement_lands_as_disagreement(store) -> None:  # type: ignore[no-untyped-def]
    candidate = store.record("TV-S1").candidate or {}
    wrong = "Tý" if candidate["THIEN_CO"] != "Tý" else "Sửu"
    row = _filled_row(store, "TV-S1", expected_THIEN_CO=wrong)
    applied = apply_import(store, preview_import(store, _to_csv([row])))
    assert applied["TV-S1"] == ReviewState.DISAGREEMENT.value


def test_import_without_the_confirmation_flag_does_not_verify(store) -> None:  # type: ignore[no-untyped-def]
    row = _filled_row(store, "TV-S1", independently_confirmed="")
    applied = apply_import(store, preview_import(store, _to_csv([row])))
    assert applied["TV-S1"] == ReviewState.IN_REVIEW.value
