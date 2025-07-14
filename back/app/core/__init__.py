"""Core модули приложения"""

# Убираем импорт error_handlers для избежания circular import
# from .error_handlers import register_exception_handlers
from .exceptions import (
    AuthenticationException,
    AuthorizationException,
    BaseApplicationException,
    BusinessLogicException,
    ConflictException,
    DatabaseException,
    ErrorCode,
    ExternalAPIException,
    GracefulDegradation,
    NotFoundException,
    RedisException,
    ValidationException,
)
from .logging import get_logger, init_default_logging

__all__ = [
    "get_logger",
    "init_default_logging",
    "register_exception_handlers",
    "BaseApplicationException",
    "ValidationException",
    "AuthenticationException",
    "AuthorizationException",
    "NotFoundException",
    "ConflictException",
    "DatabaseException",
    "RedisException",
    "ExternalAPIException",
    "BusinessLogicException",
    "GracefulDegradation",
    "ErrorCode",
]



