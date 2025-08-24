"""Обработчики исключений для FastAPI"""

import traceback
from datetime import datetime
from typing import Any, Dict

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_correlation_id, get_logger, get_user_id
from app.core.settings import settings
from app.shared.exceptions.base import BaseAppException

logger = get_logger(__name__)


def create_error_response(
    error_code: str,
    message: str,
    status_code: int,
    details: Dict[str, Any] = None,
    correlation_id: str = None,
    user_id: str = None,
) -> Dict[str, Any]:
    """Создать стандартный error response"""
    return {
        "error": error_code,
        "message": message,
        "details": details or {},
        "correlation_id": correlation_id or get_correlation_id(),
        "user_id": user_id or get_user_id(),
        "timestamp": datetime.utcnow().isoformat(),
        "status_code": status_code,
    }


async def base_app_exception_handler(
    request: Request, exc: BaseAppException
) -> JSONResponse:
    """Обработчик для базовых исключений приложения"""
    # Логируем исключение
    logger.error(
        f"Application exception: {exc.error_code}",
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        status_code=exc.status_code,
        path=request.url.path,
        method=request.method,
        exc_info=True,
    )

    # Создаем response
    response_data = exc.to_dict()
    response_data["timestamp"] = datetime.utcnow().isoformat()

    return JSONResponse(status_code=exc.status_code, content=response_data)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Обработчик для HTTP исключений"""
    logger.warning(
        f"HTTP exception: {exc.status_code}",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
        method=request.method,
    )

    # Определяем error_code по статусу
    error_codes = {
        401: "AUTH_ERROR",
        403: "AUTHORIZATION_ERROR",
        404: "RESOURCE_NOT_FOUND",
        409: "RESOURCE_CONFLICT",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMIT_ERROR",
        500: "INTERNAL_ERROR",
        502: "EXTERNAL_SERVICE_ERROR",
        503: "SERVICE_UNAVAILABLE",
    }

    error_code = error_codes.get(exc.status_code, "HTTP_ERROR")

    response_data = create_error_response(
        error_code=error_code,
        message=str(exc.detail),
        status_code=exc.status_code,
        details={"original_detail": exc.detail},
    )

    return JSONResponse(status_code=exc.status_code, content=response_data)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Обработчик для ошибок валидации Pydantic"""
    logger.warning(
        "Validation error",
        errors=exc.errors(),
        path=request.url.path,
        method=request.method,
    )

    # Форматируем ошибки валидации
    validation_errors = []
    for error in exc.errors():
        validation_errors.append(
            {
                "field": " -> ".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
                "input": error.get("input"),
            }
        )

    response_data = create_error_response(
        error_code="VALIDATION_ERROR",
        message="Validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details={"validation_errors": validation_errors},
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=response_data
    )


async def sqlalchemy_exception_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """Обработчик для ошибок SQLAlchemy"""
    logger.error(
        "Database error",
        error=str(exc),
        path=request.url.path,
        method=request.method,
        exc_info=True,
    )

    # В development показываем детали, в production - общее сообщение
    if settings.is_development:
        message = f"Database error: {str(exc)}"
        details = {"sql_error": str(exc)}
    else:
        message = "Database operation failed"
        details = {"error_type": type(exc).__name__}

    response_data = create_error_response(
        error_code="DATABASE_ERROR",
        message=message,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details=details,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=response_data
    )


async def rate_limit_exception_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """Обработчик для rate limit исключений"""
    logger.warning(
        "Rate limit exceeded",
        detail=exc.detail,
        path=request.url.path,
        method=request.method,
    )

    response_data = create_error_response(
        error_code="RATE_LIMIT_ERROR",
        message="Too many requests. Please try again later.",
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        details={"limit": exc.detail, "retry_after": getattr(exc, "retry_after", 60)},
    )

    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=response_data,
        headers={"Retry-After": str(getattr(exc, "retry_after", 60))},
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Обработчик для всех остальных исключений"""
    logger.error(
        "Unhandled exception",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        method=request.method,
        exc_info=True,
    )

    # В development показываем stack trace, в production - общее сообщение
    if settings.is_development:
        message = f"Internal server error: {str(exc)}"
        details = {
            "error_type": type(exc).__name__,
            "traceback": traceback.format_exc(),
        }
    else:
        message = "Internal server error"
        details = {"error_type": type(exc).__name__, "error_id": get_correlation_id()}

    response_data = create_error_response(
        error_code="INTERNAL_ERROR",
        message=message,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details=details,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=response_data
    )


def register_exception_handlers(app) -> None:
    """Регистрация всех обработчиков исключений"""

    # Обработчики для кастомных исключений
    app.add_exception_handler(BaseAppException, base_app_exception_handler)

    # Обработчики для FastAPI исключений
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # Обработчики для внешних библиотек
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)

    # Обработчик для всех остальных исключений
    app.add_exception_handler(Exception, general_exception_handler)

    logger.info("Exception handlers registered successfully")
