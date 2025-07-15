"""DTO запросов для работы с заданиями"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TaskAttemptCreateRequest(BaseModel):
    """Запрос на создание попытки решения задачи"""

    blockId: str = Field(..., description="ID блока задачи")
    sourceCode: str = Field(..., description="Исходный код решения")
    language: str = Field(..., description="Язык программирования")
    isSuccessful: bool = Field(default=False, description="Успешность попытки")
    attemptNumber: int = Field(..., description="Номер попытки")
    
    executionTimeMs: Optional[int] = Field(None, description="Время выполнения в мс")
    memoryUsedMB: Optional[float] = Field(None, description="Использованная память в МБ")
    errorMessage: Optional[str] = Field(None, description="Сообщение об ошибке")
    stderr: Optional[str] = Field(None, description="Вывод stderr")
    durationMinutes: Optional[int] = Field(None, description="Время решения в минутах")

    class Config:
        from_attributes = True


class TaskSolutionCreateRequest(BaseModel):
    """Запрос на создание решения задачи"""

    blockId: str = Field(..., description="ID блока задачи")
    finalCode: str = Field(..., description="Финальный код решения")
    language: str = Field(..., description="Язык программирования")
    totalAttempts: int = Field(..., description="Общее количество попыток")
    timeToSolveMinutes: int = Field(..., description="Время решения в минутах")
    firstAttempt: datetime = Field(..., description="Время первой попытки")
    solvedAt: Optional[datetime] = Field(None, description="Время решения")

    class Config:
        from_attributes = True


class TaskFilterRequest(BaseModel):
    """Запрос фильтрации заданий"""

    page: int = Field(1, ge=1, description="Номер страницы")
    limit: int = Field(10, ge=1, le=100, description="Количество заданий на странице")
    main_categories: Optional[list[str]] = Field(None, description="Основные категории")
    sub_categories: Optional[list[str]] = Field(None, description="Подкатегории")
    search_query: Optional[str] = Field(None, description="Поисковый запрос")
    sort_by: str = Field("orderInFile", description="Поле для сортировки")
    sort_order: str = Field("asc", description="Порядок сортировки")
    item_type: Optional[str] = Field(None, description="Тип элемента")
    only_unsolved: Optional[bool] = Field(None, description="Только нерешённые")
    companies: Optional[list[str]] = Field(None, description="Компании")

    class Config:
        from_attributes = True 


