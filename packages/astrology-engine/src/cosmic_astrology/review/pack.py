"""Export a review pack, and import one back.

The pack is for a practitioner who will never run this application. It carries
the birth data, what the engine produced, and **blank** expected fields. It does
not carry a suggestion: the moment the pack pre-fills an answer, the review
stops being independent and the whole exercise is theatre.
"""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from cosmic_astrology.review.model import MAJOR_STAR_CODES, FixtureReview
from cosmic_astrology.review.store import ReviewStore

__all__ = ["ImportOutcome", "export_csv", "export_json", "preview_import"]

_CSV_COLUMNS = (
    ["fixture_id", "purpose", "calendar", "birth_date", "birth_time", "gender",
     "timezone_id", "utc_offset", "lunar_date", "menh", "than", "cuc",
     "engine_tu_vi"]
    + [f"engine_{code}" for code in MAJOR_STAR_CODES]
    + ["expected_tu_vi"]
    + [f"expected_{code}" for code in MAJOR_STAR_CODES]
    + ["expected_tuan", "expected_triet", "source_id", "page", "reviewer",
       "reviewed_at", "independently_confirmed", "notes"]
)


def _row(record: Any) -> dict[str, object]:
    raw = record.raw
    inp = raw["input"]
    frame = raw.get("derived_frame") or {}
    tzc = raw.get("timezone_context") or {}
    lunar = frame.get("lunar") or {}
    candidate = record.candidate or {}

    row: dict[str, object] = {
        "fixture_id": raw["id"],
        "purpose": raw.get("purpose", ""),
        "calendar": inp["calendar"],
        "birth_date": f"{inp['day']:02d}/{inp['month']:02d}/{inp['year']}",
        "birth_time": f"{inp['hour']:02d}:{inp.get('minute', 0):02d}",
        "gender": inp["gender"],
        "timezone_id": tzc.get("timezone_id", ""),
        "utc_offset": tzc.get("utc_offset_hours", ""),
        "lunar_date": (
            f"{lunar.get('day')}/{lunar.get('month')}"
            f"{' nhuận' if lunar.get('is_leap_month') else ''}/{lunar.get('year')}"
            if lunar else "(bị chặn)"
        ),
        "menh": frame.get("menh", ""),
        "than": frame.get("than", ""),
        "cuc": frame.get("cuc", ""),
        "engine_tu_vi": candidate.get("TU_VI", ""),
    }
    for code in MAJOR_STAR_CODES:
        row[f"engine_{code}"] = candidate.get(code, "")
    # Expected columns ship empty on purpose — see the module docstring.
    row["expected_tu_vi"] = ""
    for code in MAJOR_STAR_CODES:
        row[f"expected_{code}"] = ""
    row.update(
        {
            "expected_tuan": "", "expected_triet": "", "source_id": "", "page": "",
            "reviewer": "", "reviewed_at": "", "independently_confirmed": "", "notes": "",
        }
    )
    return row


def export_csv(store: ReviewStore) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=_CSV_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for record in store.records:
        writer.writerow(_row(record))
    return buffer.getvalue()


def export_json(store: ReviewStore) -> str:
    payload = {
        "_README": (
            "Gói thẩm định Cosmic Signs. Các trường expected_* ĐỂ TRỐNG có chủ đích — "
            "bạn tra nguồn rồi điền vào. Đừng chép từ cột engine_*: nếu chép thì bản "
            "thẩm định không chứng minh được điều gì."
        ),
        "exported_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "convention_profile": store.data.get("convention_profile"),
        "convention_version": store.data.get("convention_version"),
        "star_codes": list(MAJOR_STAR_CODES),
        "sources": store.registry.to_dict(),
        "fixtures": [_row(record) for record in store.records],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


@dataclass(slots=True)
class ImportOutcome:
    """What an import *would* do. Nothing is written until it is applied."""

    accepted: dict[str, FixtureReview] = field(default_factory=dict)
    rejected: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return not self.rejected

    def to_dict(self) -> dict[str, object]:
        return {
            "accepted": {k: v.to_dict() for k, v in self.accepted.items()},
            "rejected": list(self.rejected),
            "skipped": list(self.skipped),
            "is_clean": self.is_clean,
        }


def _split_list(value: str | None) -> list[str] | None:
    """A comma-separated cell as a list, or ``None`` when the reviewer left it blank.

    Module-level on purpose: as a closure inside the import loop it captured the
    loop variable late, which is correct only by accident of when it is called.
    """
    text = (value or "").strip()
    return [part.strip() for part in text.split(",") if part.strip()] if text else None


def _truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y", "x", "có"}


def preview_import(store: ReviewStore, csv_text: str) -> ImportOutcome:
    """Validate a returned pack. Never writes; never touches candidate output."""
    outcome = ImportOutcome()
    known = {record.id for record in store.records}
    reader = csv.DictReader(io.StringIO(csv_text))

    if reader.fieldnames is None or "fixture_id" not in reader.fieldnames:
        outcome.rejected.append("Thiếu cột 'fixture_id' — file không đúng định dạng gói thẩm định.")
        return outcome

    for line_no, row in enumerate(reader, start=2):
        fixture_id = (row.get("fixture_id") or "").strip()
        if not fixture_id:
            outcome.rejected.append(f"Dòng {line_no}: thiếu fixture_id.")
            continue
        if fixture_id not in known:
            outcome.rejected.append(f"Dòng {line_no}: không có fixture '{fixture_id}'.")
            continue

        expected_stars = {
            code: (row.get(f"expected_{code}") or "").strip()
            for code in MAJOR_STAR_CODES
            if (row.get(f"expected_{code}") or "").strip()
        }
        expected_tu_vi = (row.get("expected_tu_vi") or "").strip() or None

        if not expected_stars and not expected_tu_vi:
            outcome.skipped.append(f"{fixture_id}: chưa điền gì, bỏ qua.")
            continue

        missing = [c for c in MAJOR_STAR_CODES if c not in expected_stars]
        if missing:
            outcome.rejected.append(
                f"{fixture_id}: thiếu {len(missing)} sao ({', '.join(missing[:3])}…). "
                "Một bản thẩm định dở dang không được nhận."
            )
            continue

        reviewer = (row.get("reviewer") or "").strip() or None
        source_id = (row.get("source_id") or "").strip() or None
        if not reviewer:
            outcome.rejected.append(f"{fixture_id}: thiếu tên người thẩm định.")
            continue
        if not source_id:
            outcome.rejected.append(f"{fixture_id}: thiếu source_id.")
            continue
        if store.registry.get(source_id) is None:
            outcome.rejected.append(f"{fixture_id}: nguồn '{source_id}' chưa có trong sổ nguồn.")
            continue

        outcome.accepted[fixture_id] = FixtureReview(
            expected_tu_vi=expected_tu_vi,
            expected_stars=expected_stars,
            expected_tuan=_split_list(row.get("expected_tuan")),
            expected_triet=_split_list(row.get("expected_triet")),
            independently_confirmed=_truthy(row.get("independently_confirmed")),
            reviewer=reviewer,
            reviewed_at=(row.get("reviewed_at") or "").strip()
            or datetime.now(UTC).date().isoformat(),
            source_id=source_id,
            page=(row.get("page") or "").strip() or None,
            notes=(row.get("notes") or "").strip(),
        )
    return outcome


def apply_import(store: ReviewStore, outcome: ImportOutcome) -> dict[str, str]:
    """Write an already-previewed import. Refuses a pack with any rejection."""
    if not outcome.is_clean:
        raise ValueError(
            "Gói thẩm định còn dòng bị từ chối — sửa xong rồi nhập lại, "
            "không nhập một phần."
        )
    applied: dict[str, str] = {}
    for fixture_id, review in outcome.accepted.items():
        evaluation = store.save_review(fixture_id, review)
        applied[fixture_id] = evaluation.state.value
    return applied
