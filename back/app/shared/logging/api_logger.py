"""
Унифицированное API логирование для роутеров
"""

from functools import wraps
from typing import Optional

from fastapi import Request

from app.core.logging import get_logger
from app.shared.models.user_models import User


class APILogger:
    """
    Класс для унифицированного логирования API операций
    """

    def __init__(self, module_name: str):
        self.logger = get_logger(module_name)
        self.module = module_name

    def log_operation_start(self, operation: str, **kwargs) -> None:
        """Логирование начала операции"""
        self.logger.info(
            f"API: Starting {operation}",
            extra={
                "operation": operation,
                "module": self.module,
                "stage": "start",
                **kwargs,
            },
        )

    def log_operation_success(self, operation: str, **kwargs) -> None:
        """Логирование успешного завершения операции"""
        self.logger.info(
            f"API: Successfully completed {operation}",
            extra={
                "operation": operation,
                "module": self.module,
                "stage": "success",
                **kwargs,
            },
        )

    def log_operation_error(self, operation: str, error: Exception, **kwargs) -> None:
        """Логирование ошибки операции"""
        self.logger.error(
            f"API: Error in {operation}: {str(error)}",
            extra={
                "operation": operation,
                "module": self.module,
                "stage": "error",
                "error_type": type(error).__name__,
                "error_message": str(error),
                **kwargs,
            },
        )

    def log_operation_warning(self, operation: str, message: str, **kwargs) -> None:
        """Логирование предупреждения операции"""
        self.logger.warning(
            f"API: Warning in {operation}: {message}",
            extra={
                "operation": operation,
                "module": self.module,
                "stage": "warning",
                "warning_message": message,
                **kwargs,
            },
        )

    def log_user_action(self, user: User, action: str, **kwargs) -> None:
        """Логирование действия пользователя"""
        self.logger.info(
            f"User action: {action}",
            extra={
                "user_id": user.id,
                "username": getattr(user, "username", "unknown"),
                "action": action,
                "module": self.module,
                **kwargs,
            },
        )

    def log_request_details(self, request: Request, operation: str, **kwargs) -> None:
        """Логирование деталей запроса"""
        self.logger.debug(
            f"Request details for {operation}",
            extra={
                "operation": operation,
                "module": self.module,
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown"),
                **kwargs,
            },
        )

    def log_data_access(
        self, operation: str, data_type: str, count: Optional[int] = None, **kwargs
    ) -> None:
        """Логирование доступа к данным"""
        extra_data = {
            "operation": operation,
            "module": self.module,
            "data_type": data_type,
            **kwargs,
        }

        if count is not None:
            extra_data["count"] = count

        self.logger.debug(f"Data access: {operation} {data_type}", extra=extra_data)

    def log_performance(self, operation: str, duration_ms: float, **kwargs) -> None:
        """Логирование производительности"""
        self.logger.info(
            f"Performance: {operation} took {duration_ms:.2f}ms",
            extra={
                "operation": operation,
                "module": self.module,
                "duration_ms": duration_ms,
                "performance": True,
                **kwargs,
            },
        )


def api_logger_decorator(operation_name: str, log_performance: bool = False):
    """
    Декоратор для автоматического логирования API операций

    Args:
        operation_name: Название операции
        log_performance: Логировать ли производительность

    Usage:
        @api_logger_decorator("create_user", log_performance=True)
        async def create_user_endpoint(request: CreateUserRequest):
            # Автоматическое логирование начала, завершения и ошибок
            pass
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Создаем логгер для модуля
            module_name = func.__module__
            logger = APILogger(module_name)

            # Извлекаем полезную информацию из аргументов
            request_info = {}
            user_info = {}

            # Ищем Request объект
            for arg in args:
                if isinstance(arg, Request):
                    request_info = {
                        "method": arg.method,
                        "url": str(arg.url),
                        "client_ip": arg.client.host if arg.client else "unknown",
                    }
                    break

            # Ищем User объект в kwargs
            for key, value in kwargs.items():
                if isinstance(value, User):
                    user_info = {
                        "user_id": value.id,
                        "username": getattr(value, "username", "unknown"),
                    }
                    break

            # Логируем начало операции
            logger.log_operation_start(operation_name, **request_info, **user_info)

            try:
                # Измеряем время выполнения если нужно
                if log_performance:
                    import time

                    start_time = time.time()

                # Выполняем операцию
                result = await func(*args, **kwargs)

                # Логируем производительность
                if log_performance:
                    duration_ms = (time.time() - start_time) * 1000
                    logger.log_performance(operation_name, duration_ms, **user_info)

                # Логируем успешное завершение
                logger.log_operation_success(operation_name, **user_info)

                return result

            except Exception as e:
                # Логируем ошибку
                logger.log_operation_error(operation_name, e, **user_info)
                raise

        return wrapper

    return decorator


class RequestContextLogger:
    """
    Логгер для контекста запроса
    """

    def __init__(self, request: Request, user: Optional[User] = None):
        self.request = request
        self.user = user
        self.logger = get_logger(__name__)

    def log_request_start(self) -> None:
        """Логирование начала обработки запроса"""
        self.logger.info(
            "Request started",
            extra={
                "method": self.request.method,
                "url": str(self.request.url),
                "client_ip": self.request.client.host
                if self.request.client
                else "unknown",
                "user_agent": self.request.headers.get("user-agent", "unknown"),
                "user_id": self.user.id if self.user else None,
                "username": getattr(self.user, "username", None) if self.user else None,
            },
        )

    def log_request_end(self, status_code: int) -> None:
        """Логирование завершения обработки запроса"""
        self.logger.info(
            "Request completed",
            extra={
                "method": self.request.method,
                "url": str(self.request.url),
                "status_code": status_code,
                "user_id": self.user.id if self.user else None,
            },
        )


# Готовые логгеры для разных модулей
class ModuleLoggers:
    """Фабрика логгеров для разных модулей"""

    @staticmethod
    def get_auth_logger() -> APILogger:
        return APILogger("app.features.auth")

    @staticmethod
    def get_task_logger() -> APILogger:
        return APILogger("app.features.task")

    @staticmethod
    def get_content_logger() -> APILogger:
        return APILogger("app.features.content")

    @staticmethod
    def get_theory_logger() -> APILogger:
        return APILogger("app.features.theory")

    @staticmethod
    def get_progress_logger() -> APILogger:
        return APILogger("app.features.progress")

    @staticmethod
    def get_stats_logger() -> APILogger:
        return APILogger("app.features.stats")

    @staticmethod
    def get_code_editor_logger() -> APILogger:
        return APILogger("app.features.code_editor")

    @staticmethod
    def get_mindmap_logger() -> APILogger:
        return APILogger("app.features.mindmap")

    @staticmethod
    def get_admin_logger() -> APILogger:
        return APILogger("app.features.admin")


# Специализированные декораторы для разных типов операций
def log_create_operation(resource_name: str):
    """Декоратор для логирования операций создания"""
    return api_logger_decorator(f"create_{resource_name}", log_performance=True)


def log_update_operation(resource_name: str):
    """Декоратор для логирования операций обновления"""
    return api_logger_decorator(f"update_{resource_name}", log_performance=True)


def log_delete_operation(resource_name: str):
    """Декоратор для логирования операций удаления"""
    return api_logger_decorator(f"delete_{resource_name}", log_performance=False)


def log_get_operation(resource_name: str):
    """Декоратор для логирования операций получения"""
    return api_logger_decorator(f"get_{resource_name}", log_performance=False)


def log_list_operation(resource_name: str):
    """Декоратор для логирования операций получения списков"""
    return api_logger_decorator(f"list_{resource_name}", log_performance=True)
