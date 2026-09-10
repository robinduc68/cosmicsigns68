"""FastAPI dependencies."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.chart_repository import ChartRepository
from app.services.chart_service import ChartService

DbSession = Annotated[AsyncSession, Depends(get_db)]


def get_chart_service(session: DbSession) -> ChartService:
    return ChartService(ChartRepository(session))


ChartServiceDep = Annotated[ChartService, Depends(get_chart_service)]
