"""
Request DTOs для progress feature
"""

from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, validator

from app.shared.types.common import validate_not_empty, validate_positive_int


class TaskAttemptCreateRequest(BaseModel):
    """Запрос на создание попытки решения задачи"""
    
    user_id: int = Field(..., description="ID пользователя")
    task_id: str = Field(..., description="ID задачи/блока")
    source_code: Optional[str] = Field(None, description="Исходный код решения")
    language: Optional[str] = Field(None, description="Язык программирования")
    is_successful: bool = Field(False, description="Успешность попытки")
    execution_time_ms: Optional[int] = Field(None, description="Время выполнения в мс")
    memory_used_mb: Optional[Decimal] = Field(None, description="Использованная память в МБ")
    error_message: Optional[str] = Field(None, description="Сообщение об ошибке")
    stderr: Optional[str] = Field(None, description="Стандартный поток ошибок")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Дополнительные данные")
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if v <= 0:
            raise ValueError('User ID должен быть положительным числом')
        return v
    
    @validator('task_id')
    def validate_task_id(cls, v):
        if not v or not v.strip():
            raise ValueError('Task ID не может быть пустым')
        return v.strip()
    
    @validator('execution_time_ms')
    def validate_execution_time(cls, v):
        if v is not None and v < 0:
            raise ValueError('Время выполнения не может быть отрицательным')
        return v
    
    @validator('memory_used_mb')
    def validate_memory_used(cls, v):
        if v is not None and v < 0:
            raise ValueError('Использованная память не может быть отрицательной')
        return v


class TaskSolutionCreateRequest(BaseModel):
    """Запрос на создание решения задачи"""
    
    user_id: int = Field(..., description="ID пользователя")
    task_id: str = Field(..., description="ID задачи")
    source_code: str = Field(..., description="Исходный код решения")
    language: str = Field(..., description="Язык программирования")
    execution_time_ms: Optional[int] = Field(None, description="Время выполнения в мс")
    memory_used_mb: Optional[Decimal] = Field(None, description="Использованная память в МБ")
    is_optimal: bool = Field(False, description="Является ли решение оптимальным")
    solution_rating: Optional[int] = Field(None, description="Рейтинг решения (1-5)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Дополнительные данные")
    
    @validator('user_id')
    def validate_user_id(cls, v):
        return validate_positive_int(v, "User ID")
    
    @validator('task_id')
    def validate_task_id(cls, v):
        return validate_not_empty(v, "Task ID")
    
    @validator('source_code')
    def validate_source_code(cls, v):
        return validate_not_empty(v, "Source Code")
    
    @validator('language')
    def validate_language(cls, v):
        return validate_not_empty(v, "Language")
    
    @validator('solution_rating')
    def validate_solution_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Рейтинг решения должен быть от 1 до 5')
        return v


class ContentProgressUpdateRequest(BaseModel):
    """Запрос на обновление прогресса по контенту"""
    
    user_id: int = Field(..., description="ID пользователя")
    block_id: str = Field(..., description="ID блока контента")
    is_completed: Optional[bool] = Field(None, description="Завершен ли блок")
    time_spent_minutes: Optional[int] = Field(None, description="Потраченное время в минутах")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Дополнительные данные")
    
    @validator('user_id')
    def validate_user_id(cls, v):
        return validate_positive_int(v, "User ID")
    
    @validator('block_id')
    def validate_block_id(cls, v):
        return validate_not_empty(v, "Block ID")
    
    @validator('time_spent_minutes')
    def validate_time_spent(cls, v):
        if v is not None and v < 0:
            raise ValueError('Потраченное время не может быть отрицательным')
        return v


class CategoryProgressUpdateRequest(BaseModel):
    """Запрос на обновление прогресса по категории"""
    
    user_id: int = Field(..., description="ID пользователя")
    main_category: str = Field(..., description="Основная категория")
    sub_category: Optional[str] = Field(None, description="Подкатегория")
    total_tasks: int = Field(..., description="Общее количество задач")
    completed_tasks: int = Field(..., description="Количество выполненных задач")
    attempted_tasks: int = Field(..., description="Количество попыток")
    time_spent_minutes: Optional[int] = Field(None, description="Потраченное время в минутах")
    
    @validator('user_id')
    def validate_user_id(cls, v):
        return validate_positive_int(v, "User ID")
    
    @validator('main_category')
    def validate_main_category(cls, v):
        return validate_not_empty(v, "Main Category")
    
    @validator('total_tasks')
    def validate_total_tasks(cls, v):
        if v < 0:
            raise ValueError('Общее количество задач не может быть отрицательным')
        return v
    
    @validator('completed_tasks')
    def validate_completed_tasks(cls, v):
        if v < 0:
            raise ValueError('Количество выполненных задач не может быть отрицательным')
        return v
    
    @validator('attempted_tasks')
    def validate_attempted_tasks(cls, v):
        if v < 0:
            raise ValueError('Количество попыток не может быть отрицательным')
        return v
    
    @validator('completed_tasks')
    def validate_completed_vs_total(cls, v, values):
        if 'total_tasks' in values and v > values['total_tasks']:
            raise ValueError('Количество выполненных задач не может превышать общее количество')
        return v
    
    @validator('attempted_tasks')
    def validate_attempted_vs_completed(cls, v, values):
        if 'completed_tasks' in values and v < values['completed_tasks']:
            raise ValueError('Количество попыток не может быть меньше выполненных задач')
        return v


class ProgressAnalyticsRequest(BaseModel):
    """Запрос аналитики прогресса"""
    
    user_id: Optional[int] = Field(None, description="ID пользователя (None для общей статистики)")
    category: Optional[str] = Field(None, description="Фильтр по категории")
    date_from: Optional[datetime] = Field(None, description="Дата начала периода")
    date_to: Optional[datetime] = Field(None, description="Дата окончания периода")
    limit: int = Field(20, description="Лимит результатов")
    offset: int = Field(0, description="Смещение для пагинации")
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if v is not None:
            return validate_positive_int(v, "User ID")
        return v
    
    @validator('limit')
    def validate_limit(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Лимит должен быть от 1 до 100')
        return v
    
    @validator('offset')
    def validate_offset(cls, v):
        if v < 0:
            raise ValueError('Смещение не может быть отрицательным')
        return v
    
    @validator('date_to')
    def validate_date_range(cls, v, values):
        if v and 'date_from' in values and values['date_from'] and v < values['date_from']:
            raise ValueError('Дата окончания не может быть раньше даты начала')
        return v


class UserStatsUpdateRequest(BaseModel):
    """Запрос на обновление общей статистики пользователя"""
    
    user_id: int = Field(..., description="ID пользователя")
    tasks_solved_delta: int = Field(0, description="Изменение количества решенных задач")
    time_spent_delta: int = Field(0, description="Изменение потраченного времени в минутах")
    force_recalculate: bool = Field(False, description="Принудительный пересчет всей статистики")
    
    @validator('user_id')
    def validate_user_id(cls, v):
        return validate_positive_int(v, "User ID") 


