"""Data access for charts. The service layer never writes SQL itself."""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.chart import Chart


class ChartRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, chart: Chart) -> Chart:
        self._session.add(chart)
        await self._session.commit()
        await self._session.refresh(chart)
        return chart

    async def get(self, chart_id: uuid.UUID) -> Chart | None:
        return await self._session.get(Chart, chart_id)

    async def get_by_idempotency_key(self, key: str) -> Chart | None:
        result = await self._session.execute(select(Chart).where(Chart.idempotency_key == key))
        return result.scalar_one_or_none()

    async def list_by_ids(self, chart_ids: Sequence[uuid.UUID]) -> list[Chart]:
        if not chart_ids:
            return []
        result = await self._session.execute(
            select(Chart).where(Chart.id.in_(chart_ids)).order_by(Chart.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete(self, chart_id: uuid.UUID) -> bool:
        result = await self._session.execute(delete(Chart).where(Chart.id == chart_id))
        await self._session.commit()
        return bool(result.rowcount)  # type: ignore[attr-defined]  # CursorResult at runtime
