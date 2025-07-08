"""Базовые DTO классы для устранения дублирования"""

from datetime import datetime
from typing import Generic, TypeVar, List, Dict, Any, Optional
from pydantic import BaseModel
from pydantic.generics import GenericModel

# Type variables для Generic классов
T = TypeVar('T')
ItemT = TypeVar('ItemT', bound=BaseModel)


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
    id: str


class PaginationInfo(BaseModel):
    """Информация о пагинации"""
    page: int
    limit: int
    total: int
    totalPages: int
    
    @classmethod
    def create(cls, page: int, limit: int, total: int) -> 'PaginationInfo':
        """Создание информации о пагинации"""
        total_pages = (total + limit - 1) // limit if total > 0 else 0
        return cls(
            page=page,
            limit=limit,
            total=total,
            totalPages=total_pages
        )


class PaginatedResponse(GenericModel, Generic[ItemT]):
    """Универсальный пагинированный ответ"""
    items: List[ItemT]
    pagination: PaginationInfo
    
    @classmethod
    def create(
        cls, 
        items: List[ItemT], 
        page: int, 
        limit: int, 
        total: int
    ) -> 'PaginatedResponse[ItemT]':
        """Создание пагинированного ответа"""
        pagination = PaginationInfo.create(page, limit, total)
        return cls(items=items, pagination=pagination)


class SimpleListResponse(GenericModel, Generic[T]):
    """Простой список элементов"""
    items: List[T]
    
    @classmethod
    def create(cls, items: List[T]) -> 'SimpleListResponse[T]':
        """Создание простого списка"""
        return cls(items=items)


class NamedListResponse(BaseModel):
    """Список строк с именованным полем"""
    
    @classmethod
    def create_categories(cls, categories: List[str]) -> Dict[str, List[str]]:
        """Создание ответа с категориями"""
        return {"categories": categories}
    
    @classmethod
    def create_subcategories(cls, subcategories: List[str]) -> Dict[str, List[str]]:
        """Создание ответа с подкатегориями"""
        return {"subcategories": subcategories}


class CountResponse(BaseModel):
    """Ответ с количеством"""
    count: int


class BulkActionResponse(BaseModel):
    """Ответ на массовое действие"""
    success_count: int
    failed_ids: List[str] = []
    error_messages: List[str] = []
    
    @property
    def total_processed(self) -> int:
        """Общее количество обработанных элементов"""
        return self.success_count + len(self.failed_ids)
    
    @property
    def has_errors(self) -> bool:
        """Есть ли ошибки"""
        return len(self.failed_ids) > 0


class MessageResponse(BaseModel):
    """Ответ с сообщением"""
    message: str
    
    @classmethod
    def success(cls, message: str = "Operation completed successfully") -> 'MessageResponse':
        """Создание успешного ответа"""
        return cls(message=message)
    
    @classmethod
    def error(cls, message: str) -> 'MessageResponse':
        """Создание ответа с ошибкой"""
        return cls(message=message)


# Базовые Request DTO
class CreateRequest(BaseModel):
    """Базовый запрос на создание"""
    pass


class UpdateRequest(BaseModel):
    """Базовый запрос на обновление (все поля опциональные)"""
    pass


class BulkActionRequest(BaseModel):
    """Запрос на массовое действие"""
    ids: List[str]
    
    def validate_ids(self) -> None:
        """Валидация списка ID"""
        if not self.ids:
            raise ValueError("IDs list cannot be empty")
        if len(self.ids) > 1000:  # Защита от слишком больших запросов
            raise ValueError("Too many IDs (max 1000)")


# Утилиты для миграции
class DTOMigrationHelper:
    """Помощник для постепенной миграции DTO"""
    
    @staticmethod
    def convert_legacy_pagination(
        data: List[ItemT], 
        total: int, 
        page: int, 
        limit: int,
        data_field_name: str = "data"
    ) -> Dict[str, Any]:
        """Конвертация старого формата пагинации в новый"""
        pagination_info = PaginationInfo.create(page, limit, total)
        
        return {
            data_field_name: data,
            "pagination": pagination_info.dict(),
            # Дополнительные поля для обратной совместимости
            "total": total,
            "page": page,
            "limit": limit,
            "totalPages": pagination_info.totalPages
        }
    
    @staticmethod
    def add_legacy_fields(response_dict: Dict[str, Any], **legacy_fields) -> Dict[str, Any]:
        """Добавление legacy полей для обратной совместимости"""
        result = response_dict.copy()
        result.update(legacy_fields)
        return result 