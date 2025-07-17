"""Core модули приложения"""

# Убираем импорт error_handlers для избежания circular import
# from .error_handlers import register_exception_handlers
from .exceptions import (
    GracefulDegradation,
)
from .logging import get_logger, init_default_logging

__all__ = [
    "get_logger",
    "init_default_logging",
    "GracefulDegradation",
]



