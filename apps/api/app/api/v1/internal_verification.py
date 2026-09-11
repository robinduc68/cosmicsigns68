"""Internal verification workbench — developers and reviewers only.

Not a product surface. Every route 404s in production rather than 403-ing, so a
production deployment does not even admit the endpoints exist. Nothing here is
reachable from the public site, and none of it is indexed.

The workbench never writes to the engine's candidate output. It only stores what
a reviewer asserts, in fields the engine never reads back.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from cosmic_astrology import BirthInput, build_chart
from cosmic_astrology.chart.types import CalendarType, EngineStage, Gender
from cosmic_astrology.conventions import COSMIC_SIGNS_STANDARD_V1, RuleId
from cosmic_astrology.conventions.profile import validate_convention_profile
from cosmic_astrology.review import (
    Discrepancy,
    DiscrepancyStatus,
    FixtureReview,
    Source,
    SourceType,
    apply_import,
    export_csv,
    export_json,
    load_store,
    preview_import,
    promote_rule_verification,
)
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.logging import get_logger
from app.schemas.common import success

logger = get_logger(__name__)


def require_internal_access() -> None:
    """Hide the workbench outside development.

    404 rather than 403: in production the honest answer is that this surface
    does not exist. When admin auth lands (Phase "Auth"), this is the single
    place to add an ADMIN role check.
    """
    if get_settings().is_production:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")


router = APIRouter(
    prefix="/_internal/verification",
    tags=["internal"],
    dependencies=[Depends(require_internal_access)],
    include_in_schema=False,
)

NoIndex = {"X-Robots-Tag": "noindex, nofollow"}


class ReviewInput(BaseModel):
    """Reviewer findings. Deliberately has no field for engine output."""

    expected_tu_vi: str | None = None
    expected_stars: dict[str, str] | None = None
    expected_tuan: list[str] | None = None
    expected_triet: list[str] | None = None
    independently_confirmed: bool = False
    reviewer: str | None = Field(default=None, max_length=120)
    reviewed_at: str | None = None
    source_id: str | None = None
    page: str | None = Field(default=None, max_length=40)
    notes: str = Field(default="", max_length=2000)


class SourceInput(BaseModel):
    id: str = Field(min_length=2, max_length=64)
    title: str = Field(min_length=2, max_length=300)
    source_type: str
    author: str | None = None
    edition: str | None = None
    publication_year: int | None = None
    publisher: str | None = None
    school: str | None = None
    notes: str = ""


class DiscrepancyInput(BaseModel):
    fixture_id: str
    rule_id: str
    subject: str
    candidate: str | None = None
    expected: str | None = None
    source_id: str | None = None
    reviewer: str | None = None
    notes: str = ""


class ImportInput(BaseModel):
    csv_text: str = Field(min_length=1)
    apply: bool = False


class PromoteInput(BaseModel):
    rule: str
    reviewer: str | None = None
    source_id: str | None = None
    evidence: str = ""


def _birth_from(raw: dict[str, Any]) -> BirthInput:
    return BirthInput(
        name=str(raw.get("id", "fixture")),
        gender=Gender(raw["input"]["gender"]),
        calendar_type=CalendarType(raw["input"]["calendar"]),
        day=raw["input"]["day"],
        month=raw["input"]["month"],
        year=raw["input"]["year"],
        hour=raw["input"]["hour"],
        minute=raw["input"].get("minute", 0),
        is_leap_month=raw["input"]["is_leap_month"],
        tz_offset=raw["input"].get("tz_offset", 7.0),
        timezone_id=raw["input"].get("timezone_id"),
    )


@router.get("/fixtures", summary="Danh sách ca kiểm định")
async def list_fixtures() -> dict[str, Any]:
    store = load_store()
    states = store.states()
    items = []
    for record in store.records:
        evaluation = states[record.id]
        frame = record.raw.get("derived_frame") or {}
        lunar = frame.get("lunar") or {}
        source = store.registry.get(record.review.source_id)
        items.append(
            {
                "id": record.id,
                "purpose": record.raw.get("purpose", ""),
                "birth_date": "{day:02d}/{month:02d}/{year}".format(**record.raw["input"]),
                "birth_time": "{:02d}:{:02d}".format(
                    record.raw["input"]["hour"], record.raw["input"].get("minute", 0)
                ),
                "calendar": record.raw["input"]["calendar"],
                "gender": record.raw["input"]["gender"],
                "timezone": (record.raw.get("timezone_context") or {}).get("timezone_id"),
                "utc_offset": (record.raw.get("timezone_context") or {}).get("utc_offset_hours"),
                "lunar_date": (
                    f"{lunar.get('day')}/{lunar.get('month')}"
                    f"{' nhuận' if lunar.get('is_leap_month') else ''}"
                    if lunar
                    else None
                ),
                "menh": frame.get("menh"),
                "cuc": frame.get("cuc"),
                "state": evaluation.state.value,
                "blockers": list(evaluation.blockers),
                "mismatches": list(evaluation.mismatches),
                "reviewer": record.review.reviewer,
                "source": source.to_dict() if source else None,
                "blocked_reason": record.blocked_reason,
                "is_anchor": "anchor_tu_vi" in record.raw,
            }
        )
    return success(items, {"summary": store.summary()})


@router.get("/fixtures/{fixture_id}", summary="Chi tiết một ca kiểm định")
async def fixture_detail(fixture_id: str) -> dict[str, Any]:
    store = load_store()
    try:
        record = store.record(fixture_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    evaluation = record.evaluate(store.registry)
    source = store.registry.get(record.review.source_id)

    trace: list[dict[str, Any]] = []
    palaces: list[dict[str, Any]] = []
    if record.blocked_reason is None:
        # to_dict() is typed as dict[str, object]; the payload is plain JSON-shaped data.
        chart: dict[str, Any] = build_chart(
            _birth_from(record.raw), stage=EngineStage.PREVIEW, trace=True
        ).to_dict()
        trace = chart["trace"]["steps"]
        expected = record.review.expected_stars or {}
        for palace in chart["palaces"]:
            engine_stars = [s["id"] for s in palace["major_stars"]]
            expected_stars = [c for c, branch in expected.items() if branch == palace["branch"]]
            palaces.append(
                {
                    "name": palace["name"],
                    "label": palace["label"],
                    "branch": palace["branch"],
                    "is_menh": palace["is_menh"],
                    "is_than": palace["is_than"],
                    "has_tuan": palace["has_tuan"],
                    "has_triet": palace["has_triet"],
                    "engine_stars": engine_stars,
                    "expected_stars": expected_stars if expected else None,
                    "matches": (sorted(engine_stars) == sorted(expected_stars))
                    if expected
                    else None,
                }
            )

    return success(
        {
            "id": record.id,
            "purpose": record.raw.get("purpose", ""),
            "input": record.raw["input"],
            "timezone_context": record.raw.get("timezone_context"),
            "derived_frame": record.raw.get("derived_frame"),
            "engine_candidate_stars": record.candidate,
            "review": record.review.to_dict(),
            "state": evaluation.to_dict(),
            "comparisons": record.comparisons(),
            "palaces": palaces,
            "trace": trace,
            "source": source.to_dict() if source else None,
            "blocked_reason": record.blocked_reason,
            "late_zi_demonstration": record.raw.get("late_zi_demonstration"),
            "anchor_tu_vi": record.raw.get("anchor_tu_vi"),
            "anchor_basis": record.raw.get("anchor_basis"),
        }
    )


@router.put("/fixtures/{fixture_id}/review", summary="Lưu kết quả thẩm định")
async def save_review(fixture_id: str, payload: ReviewInput) -> dict[str, Any]:
    store = load_store()
    review = FixtureReview(
        expected_tu_vi=payload.expected_tu_vi,
        expected_stars=payload.expected_stars,
        expected_tuan=payload.expected_tuan,
        expected_triet=payload.expected_triet,
        independently_confirmed=payload.independently_confirmed,
        reviewer=payload.reviewer,
        # Stamped server-side once findings exist: a review time the reviewer
        # could back-date would be no evidence at all.
        reviewed_at=payload.reviewed_at
        or (datetime.now(UTC).date().isoformat() if payload.expected_stars else None),
        source_id=payload.source_id,
        page=payload.page,
        notes=payload.notes,
    )
    try:
        evaluation = store.save_review(fixture_id, review)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    logger.info(
        "verification_review_saved",
        fixture_id=fixture_id,
        state=evaluation.state.value,
        reviewer=payload.reviewer,
    )
    return success({"state": evaluation.to_dict(), "review": review.to_dict()})


@router.get("/progress", summary="Bảng tiến độ kiểm định")
async def progress() -> dict[str, Any]:
    store = load_store()
    profile = COSMIC_SIGNS_STANDARD_V1
    validation = validate_convention_profile(profile)
    return success(
        {
            "profile": profile.profile_id,
            "version": profile.version,
            "fixtures": store.summary(),
            "rules": [profile.binding(rule).to_dict() for rule in RuleId],
            "production_ready": validation.production_ready,
            "failures": list(validation.failures),
            "primary_source": (
                store.registry.primary.to_dict() if store.registry.primary else None
            ),
            "open_discrepancies": [
                d.to_dict() for d in store.discrepancies if d.is_blocking
            ],
        }
    )


@router.get("/sources", summary="Sổ nguồn đối chiếu")
async def list_sources() -> dict[str, Any]:
    store = load_store()
    return success(
        {
            "sources": store.registry.to_dict(),
            "source_types": [t.value for t in SourceType],
        }
    )


@router.post("/sources", status_code=201, summary="Thêm nguồn đối chiếu")
async def add_source(payload: SourceInput) -> dict[str, Any]:
    store = load_store()
    try:
        source = Source(
            id=payload.id,
            title=payload.title,
            source_type=SourceType(payload.source_type),
            author=payload.author,
            edition=payload.edition,
            publication_year=payload.publication_year,
            publisher=payload.publisher,
            school=payload.school,
            notes=payload.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    store.add_source(source)
    return success(source.to_dict())


@router.post("/discrepancies", status_code=201, summary="Ghi phiếu bất đồng")
async def add_discrepancy(payload: DiscrepancyInput) -> dict[str, Any]:
    store = load_store()
    existing = len(store.discrepancies)
    discrepancy = Discrepancy(
        id=f"D{existing + 1:03d}",
        fixture_id=payload.fixture_id,
        rule_id=payload.rule_id,
        subject=payload.subject,
        candidate=payload.candidate,
        expected=payload.expected,
        source_id=payload.source_id,
        reviewer=payload.reviewer,
        recorded_at=datetime.now(UTC).isoformat(timespec="seconds"),
        notes=payload.notes,
        status=DiscrepancyStatus.OPEN,
    )
    store.add_discrepancy(discrepancy)
    logger.info("verification_discrepancy_recorded", discrepancy_id=discrepancy.id)
    return success(discrepancy.to_dict())


@router.get("/export", summary="Xuất gói thẩm định")
async def export_pack(fmt: str = "csv") -> Response:
    store = load_store()
    if fmt == "json":
        return Response(
            content=export_json(store),
            media_type="application/json",
            headers={
                **NoIndex,
                "Content-Disposition": 'attachment; filename="cosmic-signs-review-pack.json"',
            },
        )
    return Response(
        content=export_csv(store),
        media_type="text/csv; charset=utf-8",
        headers={
            **NoIndex,
            "Content-Disposition": 'attachment; filename="cosmic-signs-review-pack.csv"',
        },
    )


@router.post("/import", summary="Nhập gói thẩm định (xem trước hoặc ghi)")
async def import_pack(payload: ImportInput) -> dict[str, Any]:
    store = load_store()
    outcome = preview_import(store, payload.csv_text)
    applied: dict[str, str] = {}
    if payload.apply:
        if not outcome.is_clean:
            # Partial imports would leave the matrix half-reviewed with no record
            # of which half. Refuse the whole pack instead.
            raise HTTPException(status_code=422, detail="Gói còn dòng bị từ chối")
        applied = apply_import(store, outcome)
        logger.info("verification_pack_imported", count=len(applied))
    return success({"preview": outcome.to_dict(), "applied": applied})


@router.post("/promote", summary="Kiểm tra điều kiện nâng một quy tắc")
async def promote(payload: PromoteInput) -> dict[str, Any]:
    try:
        rule = RuleId(payload.rule)
    except ValueError as exc:
        raise HTTPException(
            status_code=422, detail=f"Quy tắc không hợp lệ: {payload.rule}"
        ) from exc

    result = promote_rule_verification(
        rule=rule,
        store=load_store(),
        profile=COSMIC_SIGNS_STANDARD_V1,
        reviewer=payload.reviewer,
        source_id=payload.source_id,
        evidence=payload.evidence,
    )
    # Never mutates the profile: the last step is a reviewed commit, on purpose.
    return success({**result.to_dict(), "applied": False})
