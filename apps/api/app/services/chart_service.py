"""Chart use-cases.

This is the only place that talks to the astrology engine. The engine itself
stays free of database, HTTP and configuration concerns.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from cosmic_astrology import (
    COSMIC_SIGNS_STANDARD_V1,
    ENGINE_VERSION,
    BirthInput,
    UnresolvedConventionError,
    build_chart,
    needs_recalculation,
)
from cosmic_astrology.chart.types import CalendarType, EngineStage, Gender
from cosmic_astrology.conventions.profile import RecalculationCheck

from app.core.config import get_settings
from app.core.errors import ChartCalculationError, NotFoundError, UnresolvedConventionApiError
from app.core.logging import get_logger
from app.db.models.chart import Chart
from app.repositories.chart_repository import ChartRepository
from app.schemas.chart import ChartCreateRequest

logger = get_logger(__name__)

#: Charts persisted before ``schema_version`` was emitted. Not a fallback for a
#: missing field — it is the actual shape those rows have.
LEGACY_CHART_SCHEMA_VERSION = 1


class ChartService:
    def __init__(self, repository: ChartRepository) -> None:
        self._repository = repository

    async def create(
        self, payload: ChartCreateRequest, idempotency_key: str | None = None
    ) -> Chart:
        if idempotency_key:
            existing = await self._repository.get_by_idempotency_key(idempotency_key)
            if existing is not None:
                logger.info("chart_create_idempotent_hit", chart_id=str(existing.id))
                return existing

        stage = EngineStage(get_settings().chart_engine_stage)
        try:
            computed = build_chart(
                BirthInput(
                    name=payload.subject_name,
                    gender=Gender(payload.gender),
                    calendar_type=CalendarType(payload.calendar_type),
                    day=payload.birth_day,
                    month=payload.birth_month,
                    year=payload.birth_year,
                    hour=payload.birth_hour,
                    minute=payload.birth_minute,
                    is_leap_month=payload.is_leap_month,
                    tz_offset=payload.tz_offset,
                    birth_place=payload.birth_place,
                    # timezone_name đã là một IANA id, nên để engine tra offset
                    # lịch sử thay vì tin vào tz_offset do client gửi.
                    timezone_id=payload.timezone_name,
                ),
                stage=stage,
            )
        except UnresolvedConventionError as exc:
            # Quy ước chưa chốt (ví dụ giờ Tý sớm). Đây không phải lỗi nhập liệu
            # của người dùng, nên trả mã riêng thay vì đổ cho họ.
            logger.warning("chart_blocked_by_convention", reason=str(exc))
            raise UnresolvedConventionApiError(str(exc)) from exc
        except ValueError as exc:
            raise ChartCalculationError(str(exc)) from exc

        chart = Chart(
            convention_profile=computed.convention_profile,
            convention_version=computed.convention_version,
            subject_name=payload.subject_name,
            relationship_label=payload.relationship_label,
            gender=payload.gender,
            calendar_type=payload.calendar_type,
            birth_day=payload.birth_day,
            birth_month=payload.birth_month,
            birth_year=payload.birth_year,
            birth_hour=payload.birth_hour,
            birth_minute=payload.birth_minute,
            is_leap_month=payload.is_leap_month,
            birth_place=payload.birth_place,
            timezone_name=payload.timezone_name,
            tz_offset=payload.tz_offset,
            note=payload.note,
            engine_stage=computed.engine_stage.value,
            engine_version=computed.engine_version,
            chart_json=computed.to_dict(),
            idempotency_key=idempotency_key,
        )
        saved = await self._repository.add(chart)
        logger.info(
            "chart_created",
            chart_id=str(saved.id),
            engine_stage=saved.engine_stage,
            convention_profile=saved.convention_profile,
            convention_version=saved.convention_version,
        )
        return saved

    def recalculation_status(self, chart: Chart) -> RecalculationCheck:
        """Whether a stored chart would come out differently if built today.

        Read-only on purpose. A chart someone has already been shown — and may have
        paid for — is never rewritten underneath them; the answer is surfaced so the
        decision to rebuild stays with a person.
        """
        return needs_recalculation(
            chart.convention_profile,
            chart.convention_version,
            COSMIC_SIGNS_STANDARD_V1,
            stored_engine_version=chart.engine_version,
            current_engine_version=ENGINE_VERSION,
        )

    def schema_version(self, chart: Chart) -> int:
        """Payload shape of a stored chart.

        Charts written before the data contract existed carry no marker; they are
        version 1 by definition rather than by guesswork, and are left untouched
        on disk. Reporting the version is what lets a reader handle both shapes
        without probing for individual fields.
        """
        stored = chart.chart_json
        if isinstance(stored, dict):
            version = stored.get("schema_version")
            if isinstance(version, int):
                return version
        return LEGACY_CHART_SCHEMA_VERSION

    async def get(self, chart_id: uuid.UUID) -> Chart:
        chart = await self._repository.get(chart_id)
        if chart is None:
            raise NotFoundError("Không tìm thấy lá số này.")
        return chart

    async def list_by_ids(self, chart_ids: Sequence[uuid.UUID]) -> list[Chart]:
        return await self._repository.list_by_ids(chart_ids)

    async def delete(self, chart_id: uuid.UUID) -> None:
        if not await self._repository.delete(chart_id):
            raise NotFoundError("Không tìm thấy lá số này.")
        logger.info("chart_deleted", chart_id=str(chart_id))
