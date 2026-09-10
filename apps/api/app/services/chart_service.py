"""Chart use-cases.

This is the only place that talks to the astrology engine. The engine itself
stays free of database, HTTP and configuration concerns.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from cosmic_astrology import BirthInput, build_chart
from cosmic_astrology.chart.types import CalendarType, EngineStage, Gender

from app.core.config import get_settings
from app.core.errors import ChartCalculationError, NotFoundError
from app.core.logging import get_logger
from app.db.models.chart import Chart
from app.repositories.chart_repository import ChartRepository
from app.schemas.chart import ChartCreateRequest

logger = get_logger(__name__)


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
                ),
                stage=stage,
            )
        except ValueError as exc:
            raise ChartCalculationError(str(exc)) from exc

        chart = Chart(
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
        logger.info("chart_created", chart_id=str(saved.id), engine_stage=saved.engine_stage)
        return saved

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
