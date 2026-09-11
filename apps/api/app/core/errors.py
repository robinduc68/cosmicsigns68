"""Domain errors and the single place where they become HTTP responses."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger
from app.schemas.common import error_response

logger = get_logger(__name__)


class AppError(Exception):
    """Base class for errors the API knows how to explain to a user."""

    code = "INTERNAL_ERROR"
    http_status = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "Có lỗi xảy ra. Bạn thử lại sau ít phút nhé."

    def __init__(self, message: str | None = None, details: dict[str, Any] | None = None) -> None:
        super().__init__(message or self.message)
        self.detail_message = message or self.message
        self.details = details or {}


class NotFoundError(AppError):
    code = "NOT_FOUND"
    http_status = status.HTTP_404_NOT_FOUND
    message = "Không tìm thấy dữ liệu bạn yêu cầu."


class ValidationError(AppError):
    code = "VALIDATION_ERROR"
    http_status = status.HTTP_422_UNPROCESSABLE_CONTENT
    message = "Thông tin bạn nhập chưa hợp lệ."


class UnresolvedConventionApiError(AppError):
    """The chart needs a Tử Vi rule Cosmic Signs has not settled yet.

    Separate from a calculation failure on purpose: nothing the user typed is
    wrong, the engine simply refuses to guess between schools.
    """

    code = "CONVENTION_UNRESOLVED"
    http_status = status.HTTP_422_UNPROCESSABLE_CONTENT
    message = (
        "Giờ sinh này rơi vào một quy ước Tử Vi mà Cosmic Signs chưa chốt, nên mình "
        "chưa lập lá số được. Mình không đoán bừa để có kết quả."
    )


class ChartCalculationError(AppError):
    code = "CHART_CALCULATION_FAILED"
    http_status = status.HTTP_422_UNPROCESSABLE_CONTENT
    message = (
        "Không lập được lá số với thông tin này. Bạn kiểm tra lại ngày giờ sinh giúp mình nhé."
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.http_status,
            content=error_response(exc.code, exc.detail_message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_error(_request: Request, exc: RequestValidationError) -> JSONResponse:
        fields = {
            ".".join(str(part) for part in err["loc"][1:]): err["msg"] for err in exc.errors()
        }
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=error_response(
                "VALIDATION_ERROR", "Thông tin bạn nhập chưa hợp lệ.", {"fields": fields}
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(
                "HTTP_ERROR" if exc.status_code != 404 else "NOT_FOUND",
                str(exc.detail),
            ),
        )

    @app.exception_handler(Exception)
    async def _unhandled(_request: Request, exc: Exception) -> JSONResponse:
        logger.error("unhandled_exception", error=str(exc), error_type=type(exc).__name__)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("INTERNAL_ERROR", AppError.message),
        )
