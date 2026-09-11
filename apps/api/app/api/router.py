from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import charts, internal_verification, products

api_router = APIRouter()
api_router.include_router(charts.router)
api_router.include_router(products.router)
# Nội bộ: tự 404 khi APP_ENV=production, không nằm trong OpenAPI công khai.
api_router.include_router(internal_verification.router)
