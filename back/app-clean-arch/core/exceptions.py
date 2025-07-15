"""Централизованная система исключений и обработки ошибок"""

from enum import Enum
from typing import Any, Dict, Optional

import redis
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError

from .logging import get_logger

logger = get_logger(__name__)


class ErrorCode(str, Enum):
    """Коды ошибок для идентификации типов проблем"""

    # Общие ошибки
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"

    # Аутентификация и авторизация
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    SESSION_EXPIRED = "SESSION_EXPIRED"

    # Ресурсы
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"

    # База данных
    DATABASE_ERROR = "DATABASE_ERROR"
    CONSTRAINT_VIOLATION = "CONSTRAINT_VIOLATION"

    # Внешние сервисы
    REDIS_ERROR = "REDIS_ERROR"
    EXTERNAL_API_ERROR = "EXTERNAL_API_ERROR"

    # Бизнес-логика
    INVALID_OPERATION = "INVALID_OPERATION"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"


class BaseApplicationException(Exception):
    """Базовое исключение приложения"""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        details: Optional[Dict[str, Any]] = None,
        http_status: int = 500,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.http_status = http_status
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Конвертация в словарь для JSON response"""
        return {
            "error": {
                "code": self.error_code.value,
                "message": self.message,
                "details": self.details,
            }
        }


# Специфические исключения


class ValidationException(BaseApplicationException):
    """Ошибка валидации данных"""

    def __init__(
        self, message: str, field: Optional[str] = None, details: Optional[Dict] = None
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            details={"field": field, **(details or {})},
            http_status=400,
        )


class AuthenticationException(BaseApplicationException):
    """Ошибка аутентификации"""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message, error_code=ErrorCode.UNAUTHORIZED, http_status=401
        )


class AuthorizationException(BaseApplicationException):
    """Ошибка авторизации"""

    def __init__(self, message: str = "Access forbidden"):
        super().__init__(
            message=message, error_code=ErrorCode.FORBIDDEN, http_status=403
        )


class NotFoundException(BaseApplicationException):
    """Ресурс не найден"""

    def __init__(self, resource: str, identifier: Optional[str] = None):
        message = f"{resource} not found"
        if identifier:
            message += f" (ID: {identifier})"

        super().__init__(
            message=message,
            error_code=ErrorCode.NOT_FOUND,
            details={"resource": resource, "identifier": identifier},
            http_status=404,
        )


class ConflictException(BaseApplicationException):
    """Конфликт - ресурс уже существует"""

    def __init__(self, resource: str, identifier: Optional[str] = None):
        message = f"{resource} already exists"
        if identifier:
            message += f" ({identifier})"

        super().__init__(
            message=message,
            error_code=ErrorCode.ALREADY_EXISTS,
            details={"resource": resource, "identifier": identifier},
            http_status=409,
        )


class DatabaseException(BaseApplicationException):
    """Ошибка базы данных"""

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        details: Optional[Dict] = None,
    ):
        super().__init__(
            message=f"Database error: {message}",
            error_code=ErrorCode.DATABASE_ERROR,
            details={"operation": operation, **(details or {})},
            http_status=500,
        )


class RedisException(BaseApplicationException):
    """Ошибка Redis"""

    def __init__(self, message: str, operation: Optional[str] = None):
        super().__init__(
            message=f"Redis error: {message}",
            error_code=ErrorCode.REDIS_ERROR,
            details={"operation": operation},
            http_status=500,
        )


class ExternalAPIException(BaseApplicationException):
    """Ошибка внешнего API"""

    def __init__(self, service: str, message: str, status_code: Optional[int] = None):
        super().__init__(
            message=f"External API error ({service}): {message}",
            error_code=ErrorCode.EXTERNAL_API_ERROR,
            details={"service": service, "external_status": status_code},
            http_status=502,
        )


class BusinessLogicException(BaseApplicationException):
    """Ошибка бизнес-логики"""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_OPERATION,
            details=details,
            http_status=400,
        )


# Утилиты для graceful degradation


class GracefulDegradation:
    """Помощник для graceful degradation при ошибках внешних сервисов"""

    @staticmethod
    def handle_redis_error(
        operation: str, error: Exception, default_value: Any = None
    ) -> Any:
        """Обработка Redis ошибок с graceful degradation"""
        logger.error(
            f"Redis error in {operation}: {error}",
            extra={
                "operation": operation,
                "error_type": type(error).__name__,
                "error_message": str(error),
            },
        )
        return default_value

    @staticmethod
    def handle_external_api_error(
        service: str, error: Exception, default_value: Any = None
    ) -> Any:
        """Обработка ошибок внешних API с graceful degradation"""
        logger.error(
            f"External API error ({service}): {error}",
            extra={
                "service": service,
                "error_type": type(error).__name__,
                "error_message": str(error),
            },
        )
        return default_value


# Exception mapping utilities


def map_sqlalchemy_error(error: Exception) -> BaseApplicationException:
    """Маппинг SQLAlchemy ошибок в специфические исключения"""

    if isinstance(error, IntegrityError):
        # Парсим constraint нарушения
        error_msg = str(error.orig) if hasattr(error, "orig") else str(error)

        if "unique" in error_msg.lower() or "duplicate" in error_msg.lower():
            return ConflictException("Resource", "constraint violation")
        else:
            return DatabaseException(
                message="Constraint violation",
                operation="database_operation",
                details={"constraint_error": error_msg},
            )

    elif isinstance(error, NoResultFound):
        return NotFoundException("Resource")

    elif isinstance(error, SQLAlchemyError):
        return DatabaseException(message=str(error), operation="database_operation")

    # Fallback
    return DatabaseException(message="An unexpected database error occurred")


def map_redis_error(error: Exception) -> RedisException:
    """Маппинг Redis ошибок"""

    if isinstance(error, redis.ConnectionError):
        return RedisException(message="Could not connect to Redis", operation="connect")

    elif isinstance(error, redis.TimeoutError):
        return RedisException("Operation timeout", "redis_timeout")
    elif isinstance(error, redis.RedisError):
        return RedisException(str(error), "redis_operation")
    else:
        return RedisException(f"Unexpected Redis error: {str(error)}", "redis_unknown")
