"""FastAPI dependencies."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.chart_repository import ChartRepository
from app.repositories.product_repository import ProductRepository
from app.services.chart_service import ChartService
from app.services.product_service import ProductService

DbSession = Annotated[AsyncSession, Depends(get_db)]


def get_chart_service(session: DbSession) -> ChartService:
    return ChartService(ChartRepository(session))


ChartServiceDep = Annotated[ChartService, Depends(get_chart_service)]


def get_product_service(session: DbSession) -> ProductService:
    return ProductService(ProductRepository(session))


ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]
