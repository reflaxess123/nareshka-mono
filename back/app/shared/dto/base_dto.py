"""Базовые DTO классы для устранения дублирования"""

from datetime import datetime
from typing import Any, Dict, Generic, List, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

# Type variables для Generic классов
T = TypeVar("T")
ItemT = TypeVar("ItemT", bound=BaseModel)


class BaseResponse(BaseModel):
    """Базовый Response DTO с общими настройками"""

    class Config:
        from_attributes = True


class TimestampedResponse(BaseResponse):
    """Response DTO с временными метками"""

    createdAt: datetime
    updatedAt: datetime


class IdentifiedResponse(TimestampedResponse):
    """Response DTO с ID и временными метками"""

    id: int


class StringIdentifiedResponse(TimestampedResponse):
    """Response DTO с строковым ID и временными метками"""

    id: str


class PaginationInfo(BaseModel):
    """Информация о пагинации"""

    page: int
    limit: int
    total: int
    totalPages: int

    @classmethod
    def create(cls, page: int, limit: int, total: int) -> "PaginationInfo":
        """Создание информации о пагинации"""
        total_pages = (total + limit - 1) // limit if total > 0 else 0
        return cls(page=page, limit=limit, total=total, totalPages=total_pages)


class PaginatedResponse(GenericModel, Generic[ItemT]):
    """Универсальный пагинированный ответ"""

    items: List[ItemT]
    pagination: PaginationInfo

    @classmethod
    def create(
        cls, items: List[ItemT], page: int, limit: int, total: int
    ) -> "PaginatedResponse[ItemT]":
        """Создание пагинированного ответа"""
        pagination = PaginationInfo.create(page, limit, total)
        return cls(items=items, pagination=pagination)


class CategoriesResponse(BaseModel):
    """Ответ со списком категорий"""
    
    categories: List[str]

    @classmethod
    def create(cls, categories: List[str]) -> "CategoriesResponse":
        """Создание ответа с категориями"""
        return cls(categories=categories)


class SubcategoriesResponse(BaseModel):
    """Ответ со списком подкатегорий"""
    
    subcategories: List[str]

    @classmethod
    def create(cls, subcategories: List[str]) -> "SubcategoriesResponse":
        """Создание ответа с подкатегориями"""
        return cls(subcategories=subcategories)


class CountResponse(BaseModel):
    """Ответ с количеством"""

    count: int


class MessageResponse(BaseModel):
    """Ответ с сообщением"""

    message: str

    @classmethod
    def success(
        cls, message: str = "Operation completed successfully"
    ) -> "MessageResponse":
        """Создание успешного ответа"""
        return cls(message=message)

    @classmethod
    def error(cls, message: str) -> "MessageResponse":
        """Создание ответа с ошибкой"""
        return cls(message=message)


class BulkActionRequest(BaseModel):
    """Запрос на массовое действие"""

    ids: List[int]

    def validate_ids(self) -> None:
        """Валидация списка ID"""
        if not self.ids:
            raise ValueError("IDs list cannot be empty")
        if len(self.ids) > 1000:  # Защита от слишком больших запросов
            raise ValueError("Too many IDs (max 1000)")


