"""Централизованные обработчики ошибок для FastAPI"""

import traceback
from typing import Union

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
import redis

from .exceptions import (
    BaseApplicationException,
    ValidationException,
    DatabaseException,
    RedisException,
    map_sqlalchemy_error,
    map_redis_error,
    ErrorCode
)
from .logging import get_logger

logger = get_logger(__name__)


async def base_application_exception_handler(
    request: Request, 
    exc: BaseApplicationException
) -> JSONResponse:
    """Обработчик для базовых исключений приложения"""
    
    logger.error(f"Application exception: {exc.message}", extra={
        "error_code": exc.error_code.value,
        "http_status": exc.http_status,
        "details": exc.details,
        "request_url": str(request.url),
        "request_method": request.method
    })
    
    return JSONResponse(
        status_code=exc.http_status,
        content=exc.to_dict()
    )


async def sqlalchemy_exception_handler(
    request: Request, 
    exc: SQLAlchemyError
) -> JSONResponse:
    """Обработчик для SQLAlchemy ошибок"""
    
    logger.error(f"Database error: {str(exc)}", extra={
        "exception_type": type(exc).__name__,
        "request_url": str(request.url),
        "request_method": request.method,
        "traceback": traceback.format_exc()
    })
    
    # Конвертируем в специфическое исключение
    app_exception = map_sqlalchemy_error(exc)
    
    return JSONResponse(
        status_code=app_exception.http_status,
        content=app_exception.to_dict()
    )


async def redis_exception_handler(
    request: Request, 
    exc: redis.RedisError
) -> JSONResponse:
    """Обработчик для Redis ошибок"""
    
    logger.error(f"Redis error: {str(exc)}", extra={
        "exception_type": type(exc).__name__,
        "request_url": str(request.url),
        "request_method": request.method
    })
    
    # Конвертируем в специфическое исключение
    app_exception = map_redis_error(exc)
    
    return JSONResponse(
        status_code=app_exception.http_status,
        content=app_exception.to_dict()
    )


async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    """Обработчик для ошибок валидации Pydantic"""
    
    logger.warning(f"Validation error: {exc.errors()}", extra={
        "request_url": str(request.url),
        "request_method": request.method,
        "validation_errors": exc.errors()
    })
    
    # Форматируем ошибки валидации
    formatted_errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        formatted_errors.append({
            "field": field_path,
            "message": error["msg"],
            "type": error["type"]
        })
    
    validation_exc = ValidationException(
        message="Request validation failed",
        details={"validation_errors": formatted_errors}
    )
    
    return JSONResponse(
        status_code=validation_exc.http_status,
        content=validation_exc.to_dict()
    )


async def http_exception_handler(
    request: Request, 
    exc: Union[HTTPException, StarletteHTTPException]
) -> JSONResponse:
    """Обработчик для HTTP исключений"""
    
    logger.warning(f"HTTP exception: {exc.detail}", extra={
        "status_code": exc.status_code,
        "request_url": str(request.url),
        "request_method": request.method
    })
    
    # Определяем error code на основе status code
    error_code_map = {
        401: ErrorCode.UNAUTHORIZED,
        403: ErrorCode.FORBIDDEN,
        404: ErrorCode.NOT_FOUND,
        409: ErrorCode.ALREADY_EXISTS,
        422: ErrorCode.VALIDATION_ERROR,
        500: ErrorCode.INTERNAL_ERROR
    }
    
    error_code = error_code_map.get(exc.status_code, ErrorCode.INTERNAL_ERROR)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": error_code.value,
                "message": exc.detail,
                "details": {}
            }
        }
    )


async def general_exception_handler(
    request: Request, 
    exc: Exception
) -> JSONResponse:
    """Обработчик для всех остальных исключений"""
    
    logger.error(f"Unhandled exception: {str(exc)}", extra={
        "exception_type": type(exc).__name__,
        "request_url": str(request.url),
        "request_method": request.method,
        "traceback": traceback.format_exc()
    })
    
    # В production не показываем детали ошибки
    from ...config import new_settings
    
    if new_settings.server.debug:
        error_details = {
            "exception_type": type(exc).__name__,
            "traceback": traceback.format_exc()
        }
        message = f"Internal server error: {str(exc)}"
    else:
        error_details = {}
        message = "Internal server error"
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": ErrorCode.INTERNAL_ERROR.value,
                "message": message,
                "details": error_details
            }
        }
    )


def register_exception_handlers(app):
    """Регистрация всех обработчиков исключений в FastAPI приложении"""
    
    # Наши специфические исключения (наивысший приоритет)
    app.add_exception_handler(BaseApplicationException, base_application_exception_handler)
    
    # Database исключения
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    
    # Redis исключения
    app.add_exception_handler(redis.RedisError, redis_exception_handler)
    
    # FastAPI исключения
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    # Общий обработчик (самый низкий приоритет)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers registered successfully") 