"""
Исключения для progress модуля
"""

from app.shared.exceptions.base import (
    BusinessLogicException,
    ConflictError,
    NotFoundError,
    ValidationError,
)

# === Progress Data Exceptions ===


class ProgressNotFoundError(NotFoundError):
    """Прогресс не найден"""

    pass


class AttemptNotFoundError(NotFoundError):
    """Попытка не найдена"""

    pass


class SolutionNotFoundError(NotFoundError):
    """Решение не найдено"""

    pass


# === Validation Exceptions ===


class InvalidProgressDataError(ValidationError):
    """Некорректные данные прогресса"""

    pass


class InvalidAttemptDataError(ValidationError):
    """Некорректные данные попытки"""

    pass


class InvalidSolutionDataError(ValidationError):
    """Некорректные данные решения"""

    pass


class InvalidTaskIdError(ValidationError):
    """Некорректный ID задачи"""

    pass


class InvalidCategoryError(ValidationError):
    """Некорректная категория"""

    pass


# === Business Logic Exceptions ===


class ProgressUpdateError(BusinessLogicException):
    """Ошибка обновления прогресса"""

    pass


class AttemptCreationError(BusinessLogicException):
    """Ошибка создания попытки"""

    pass


class SolutionCreationError(BusinessLogicException):
    """Ошибка создания решения"""

    pass


class CategoryProgressError(BusinessLogicException):
    """Ошибка прогресса по категории"""

    pass


class ContentProgressError(BusinessLogicException):
    """Ошибка прогресса по контенту"""

    pass


# === Constraint Exceptions ===


class DuplicateAttemptError(ConflictError):
    """Дублирующаяся попытка"""

    pass


class DuplicateSolutionError(ConflictError):
    """Дублирующееся решение"""

    pass


class ProgressConflictError(ConflictError):
    """Конфликт прогресса"""

    pass


# === Analytics Exceptions ===


class AnalyticsError(BusinessLogicException):
    """Ошибка аналитики"""

    pass


class StatisticsError(BusinessLogicException):
    """Ошибка статистики"""

    pass


class ReportGenerationError(BusinessLogicException):
    """Ошибка генерации отчета"""

    pass
