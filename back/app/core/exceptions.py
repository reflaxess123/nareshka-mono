"""Централизованная система исключений и обработки ошибок"""

from typing import Any

from .logging import get_logger

logger = get_logger(__name__)


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
