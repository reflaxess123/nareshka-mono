"""Исключения для работы со статистикой"""

from app.core.exceptions import BaseApplicationException, NotFoundException


class StatsError(BaseApplicationException):
    """Базовое исключение для работы со статистикой"""
    
    def __init__(self, message: str = "Ошибка при работе со статистикой", details: str = None):
        from app.core.exceptions import ErrorCode
        super().__init__(message, ErrorCode.INTERNAL_ERROR, details, 500)


class StatsCalculationError(StatsError):
    """Исключение при ошибке вычисления статистики"""
    
    def __init__(self, calculation_type: str, message: str = None):
        error_message = f"Ошибка вычисления статистики '{calculation_type}'"
        if message:
            error_message += f": {message}"
        super().__init__(error_message)


class StatsDataNotFoundError(NotFoundException):
    """Исключение при отсутствии данных для статистики"""
    
    def __init__(self, user_id: int, stats_type: str = "statistics"):
        super().__init__(f"Данные статистики '{stats_type}' для пользователя {user_id}")


class StatsAggregationError(StatsError):
    """Исключение при ошибке агрегации данных"""
    
    def __init__(self, source: str, message: str = None):
        error_message = f"Ошибка агрегации данных из источника '{source}'"
        if message:
            error_message += f": {message}"
        super().__init__(error_message)


class StatsPermissionError(StatsError):
    """Исключение при недостатке прав для получения статистики"""
    
    def __init__(self, user_id: int, requested_stats: str):
        super().__init__(f"Пользователь {user_id} не имеет прав для получения статистики '{requested_stats}'") 


