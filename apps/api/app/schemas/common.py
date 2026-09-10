"""The single response envelope used by every endpoint: ``{data, meta, error}``."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ErrorBody(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = {}


class ApiResponse[T](BaseModel):
    data: T | None = None
    meta: dict[str, Any] = {}
    error: ErrorBody | None = None


def success(data: Any, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"data": data, "meta": meta or {}, "error": None}


def error_response(
    code: str, message: str, details: dict[str, Any] | None = None
) -> dict[str, Any]:
    return {
        "data": None,
        "meta": {},
        "error": {"code": code, "message": message, "details": details or {}},
    }
