from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import charts

api_router = APIRouter()
api_router.include_router(charts.router)
