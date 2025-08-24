"""
Response DTOs для progress feature
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TaskAttemptResponse(BaseModel):
    """Ответ с информацией о попытке решения задачи"""

    id: str = Field(..., description="ID попытки")
    user_id: int = Field(..., description="ID пользователя")
    task_id: str = Field(..., description="ID задачи")
    source_code: Optional[str] = Field(None, description="Исходный код решения")
    language: Optional[str] = Field(None, description="Язык программирования")
    result: str = Field(..., description="Результат выполнения")
    is_successful: bool = Field(..., description="Успешность попытки")
    execution_time_ms: Optional[int] = Field(None, description="Время выполнения в мс")
    memory_used_mb: Optional[Decimal] = Field(
        None, description="Использованная память в МБ"
    )
    error_message: Optional[str] = Field(None, description="Сообщение об ошибке")
    stderr: Optional[str] = Field(None, description="Стандартный поток ошибок")
    attempt_number: int = Field(..., description="Номер попытки")
    duration_minutes: Optional[float] = Field(
        None, description="Длительность в минутах"
    )
    created_at: datetime = Field(..., description="Время создания")
    updated_at: datetime = Field(..., description="Время обновления")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Дополнительные данные"
    )

    class Config:
        from_attributes = True


class TaskSolutionResponse(BaseModel):
    """Ответ с информацией о решении задачи"""

    id: str = Field(..., description="ID решения")
    user_id: int = Field(..., description="ID пользователя")
    task_id: str = Field(..., description="ID задачи")
    source_code: str = Field(..., description="Исходный код решения")
    language: str = Field(..., description="Язык программирования")
    best_execution_time_ms: Optional[int] = Field(
        None, description="Лучшее время выполнения"
    )
    best_memory_used_mb: Optional[Decimal] = Field(None, description="Лучшая память")
    total_attempts: int = Field(..., description="Общее количество попыток")
    is_optimal: bool = Field(..., description="Является ли решение оптимальным")
    solution_rating: Optional[int] = Field(None, description="Рейтинг решения")
    created_at: datetime = Field(..., description="Время создания")
    updated_at: datetime = Field(..., description="Время обновления")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Дополнительные данные"
    )

    class Config:
        from_attributes = True


class CategoryProgressResponse(BaseModel):
    """Ответ с прогрессом по категории"""

    id: str = Field(..., description="ID записи прогресса")
    user_id: int = Field(..., description="ID пользователя")
    main_category: str = Field(..., description="Основная категория")
    sub_category: Optional[str] = Field(None, description="Подкатегория")
    total_tasks: int = Field(..., description="Общее количество задач")
    completed_tasks: int = Field(..., description="Количество выполненных задач")
    attempted_tasks: int = Field(..., description="Количество попыток")
    average_attempts: Decimal = Field(..., description="Среднее количество попыток")
    total_time_spent_minutes: int = Field(..., description="Общее время в минутах")
    success_rate: Decimal = Field(..., description="Процент успеха")
    completion_percentage: float = Field(..., description="Процент завершения")
    status: str = Field(..., description="Статус прогресса")
    display_name: str = Field(..., description="Отображаемое имя")
    first_attempt: Optional[datetime] = Field(None, description="Первая попытка")
    last_activity: Optional[datetime] = Field(None, description="Последняя активность")
    created_at: datetime = Field(..., description="Время создания")
    updated_at: datetime = Field(..., description="Время обновления")

    class Config:
        from_attributes = True


class ContentProgressResponse(BaseModel):
    """Ответ с прогрессом по контенту"""

    id: str = Field(..., description="ID записи прогресса")
    user_id: int = Field(..., description="ID пользователя")
    block_id: str = Field(..., description="ID блока контента")
    solved_count: int = Field(..., description="Количество решений")
    attempt_count: int = Field(..., description="Количество попыток")
    is_completed: bool = Field(..., description="Завершен ли блок")
    status: str = Field(..., description="Статус прогресса")
    first_attempt_at: Optional[datetime] = Field(None, description="Первая попытка")
    last_attempt_at: Optional[datetime] = Field(None, description="Последняя попытка")
    completion_time_minutes: Optional[int] = Field(None, description="Время завершения")
    created_at: datetime = Field(..., description="Время создания")
    updated_at: datetime = Field(..., description="Время обновления")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Дополнительные данные"
    )

    class Config:
        from_attributes = True


class UserProgressSummaryResponse(BaseModel):
    """Сводка прогресса пользователя"""

    user_id: int = Field(..., description="ID пользователя")
    total_tasks_solved: int = Field(..., description="Общее количество решенных задач")
    total_attempts: int = Field(..., description="Общее количество попыток")
    total_time_spent_minutes: int = Field(..., description="Общее время в минутах")
    overall_success_rate: Decimal = Field(..., description="Общий процент успеха")
    categories_started: int = Field(..., description="Начатых категорий")
    categories_completed: int = Field(..., description="Завершенных категорий")
    current_streak: int = Field(..., description="Текущая серия")
    longest_streak: int = Field(..., description="Самая длинная серия")
    last_activity: Optional[datetime] = Field(None, description="Последняя активность")
    registration_date: datetime = Field(..., description="Дата регистрации")


class CategoryProgressSummaryResponse(BaseModel):
    """Краткая сводка прогресса по категории"""

    main_category: str = Field(..., description="Основная категория")
    sub_category: Optional[str] = Field(None, description="Подкатегория")
    completed_tasks: int = Field(..., description="Выполненных задач")
    total_tasks: int = Field(..., description="Общее количество задач")
    completion_percentage: float = Field(..., description="Процент завершения")
    status: str = Field(..., description="Статус прогресса")
    last_activity: Optional[datetime] = Field(None, description="Последняя активность")


class GroupedCategoryProgressResponse(BaseModel):
    """Группированный прогресс по основной категории"""

    main_category: str = Field(..., description="Основная категория")
    total_completed: int = Field(..., description="Общее количество выполненных")
    total_tasks: int = Field(..., description="Общее количество задач")
    overall_completion_percentage: float = Field(
        ..., description="Общий процент завершения"
    )
    sub_categories: List[CategoryProgressSummaryResponse] = Field(
        ..., description="Подкатегории"
    )
    last_activity: Optional[datetime] = Field(None, description="Последняя активность")


class ProgressAnalyticsResponse(BaseModel):
    """Ответ с аналитикой прогресса"""

    total_users: int = Field(..., description="Общее количество пользователей")
    active_users_today: int = Field(..., description="Активные пользователи сегодня")
    active_users_week: int = Field(..., description="Активные пользователи за неделю")
    total_tasks_solved: int = Field(..., description="Общее количество решенных задач")
    total_attempts: int = Field(..., description="Общее количество попыток")
    average_success_rate: Decimal = Field(..., description="Средний процент успеха")
    most_popular_categories: List[str] = Field(..., description="Популярные категории")
    most_difficult_tasks: List[str] = Field(..., description="Сложные задачи")
    generated_at: datetime = Field(..., description="Время генерации отчета")


class RecentActivityResponse(BaseModel):
    """Ответ с недавней активностью"""

    user_id: int = Field(..., description="ID пользователя")
    activity_type: str = Field(..., description="Тип активности")
    description: str = Field(..., description="Описание активности")
    task_id: Optional[str] = Field(None, description="ID задачи")
    category: Optional[str] = Field(None, description="Категория")
    timestamp: datetime = Field(..., description="Время активности")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Дополнительные данные"
    )


class UserDetailedProgressResponse(BaseModel):
    """Детальный прогресс пользователя"""

    user_summary: UserProgressSummaryResponse = Field(
        ..., description="Сводка пользователя"
    )
    category_progress: List[CategoryProgressResponse] = Field(
        ..., description="Прогресс по категориям"
    )
    grouped_categories: List[GroupedCategoryProgressResponse] = Field(
        ..., description="Группированные категории"
    )
    recent_activity: List[RecentActivityResponse] = Field(
        ..., description="Недавняя активность"
    )
    achievements: List[str] = Field(..., description="Достижения")
    recommendations: List[str] = Field(..., description="Рекомендации")


class ProgressStatsResponse(BaseModel):
    """Статистика прогресса"""

    period: str = Field(..., description="Период статистики")
    tasks_solved: int = Field(..., description="Решенных задач")
    time_spent_hours: float = Field(..., description="Потраченных часов")
    success_rate: Decimal = Field(..., description="Процент успеха")
    improvement_rate: Optional[Decimal] = Field(None, description="Темп улучшения")
    streak_days: int = Field(..., description="Дней подряд")
    categories_active: int = Field(..., description="Активных категорий")


class TaskProgressListResponse(BaseModel):
    """Список прогресса по задачам"""

    items: List[ContentProgressResponse] = Field(..., description="Элементы прогресса")
    total: int = Field(..., description="Общее количество")
    page: int = Field(..., description="Номер страницы")
    size: int = Field(..., description="Размер страницы")
    has_next: bool = Field(..., description="Есть ли следующая страница")


class AttemptHistoryResponse(BaseModel):
    """История попыток"""

    task_id: str = Field(..., description="ID задачи")
    user_id: int = Field(..., description="ID пользователя")
    attempts: List[TaskAttemptResponse] = Field(..., description="Список попыток")
    total_attempts: int = Field(..., description="Общее количество попыток")
    successful_attempts: int = Field(..., description="Успешных попыток")
    best_time_ms: Optional[int] = Field(None, description="Лучшее время")
    first_success_attempt: Optional[int] = Field(
        None, description="Номер первой успешной попытки"
    )
    solution: Optional[TaskSolutionResponse] = Field(
        None, description="Финальное решение"
    )
