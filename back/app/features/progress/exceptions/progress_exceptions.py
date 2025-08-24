"""
Исключения для progress модуля
"""

from app.shared.exceptions.base import (
    BusinessLogicException,
    NotFoundError,
    ValidationError,
)


class InvalidProgressDataError(ValidationError):
    """Некорректные данные прогресса"""

    pass


class ProgressNotFoundError(NotFoundError):
    """Прогресс не найден"""

    pass


class ProgressUpdateError(BusinessLogicException):
    """Ошибка обновления прогресса"""

    pass
