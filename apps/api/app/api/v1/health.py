"""Liveness and readiness probes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app.api.deps import DbSession
from app.core.config import get_settings
from app.schemas.common import success

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness — the process is up")
async def health() -> dict[str, Any]:
    settings = get_settings()
    return success({"status": "ok", "app": settings.app_name, "env": settings.app_env})


@router.get("/ready", summary="Readiness — dependencies answer")
async def ready(session: DbSession, response: Response) -> dict[str, Any]:
    checks: dict[str, str] = {}
    try:
        await session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "unavailable"

    healthy = all(value == "ok" for value in checks.values())
    if not healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return success({"status": "ready" if healthy else "degraded", "checks": checks})
