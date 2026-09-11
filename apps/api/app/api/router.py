from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import charts, products

api_router = APIRouter()
api_router.include_router(charts.router)
api_router.include_router(products.router)
