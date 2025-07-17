"""Исключения для работы со статистикой"""

from app.shared.exceptions.base import BaseAppException, ResourceNotFoundException, AuthorizationException


class StatsError(BaseAppException):
    """Базовое исключение для работы со статистикой"""
    
    def __init__(self, message: str = "Ошибка при работе со статистикой", details: dict = None):
        super().__init__(
            message=message,
            error_code="STATS_ERROR",
            status_code=500,
            details=details,
            user_message=message
        )


class StatsCalculationError(StatsError):
    """Исключение при ошибке вычисления статистики"""
    
    def __init__(self, calculation_type: str, message: str = None):
        error_message = f"Ошибка вычисления статистики '{calculation_type}'"
        if message:
            error_message += f": {message}"
        super().__init__(
            message=error_message,
            details={"calculation_type": calculation_type, "error_details": message}
        )


class StatsDataNotFoundError(ResourceNotFoundException):
    """Исключение при отсутствии данных для статистики"""
    
    def __init__(self, user_id: int, stats_type: str = "statistics"):
        super().__init__(
            resource_type="Stats",
            resource_id=f"user-{user_id}-{stats_type}",
            message=f"Данные статистики '{stats_type}' для пользователя {user_id}",
            details={"user_id": user_id, "stats_type": stats_type}
        )


class StatsAggregationError(StatsError):
    """Исключение при ошибке агрегации данных"""
    
    def __init__(self, source: str, message: str = None):
        error_message = f"Ошибка агрегации данных из источника '{source}'"
        if message:
            error_message += f": {message}"
        super().__init__(
            message=error_message,
            details={"source": source, "error_details": message}
        )


class StatsPermissionError(AuthorizationException):
    """Исключение при недостатке прав для получения статистики"""
    
    def __init__(self, user_id: int, requested_stats: str):
        super().__init__(
            message=f"Пользователь {user_id} не имеет прав для получения статистики '{requested_stats}'",
            details={"user_id": user_id, "requested_stats": requested_stats}
        ) 


