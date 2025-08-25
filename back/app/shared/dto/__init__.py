"""Shared DTOs - общие типы данных для всего приложения"""

from .base_dto import (
    BaseResponse,
    BulkActionRequest,
    CategoriesResponse,
    CountResponse,
    IdentifiedResponse,
    MessageResponse,
    PaginatedResponse,
    StringIdentifiedResponse,
    SubcategoriesResponse,
    TimestampedResponse,
)

__all__ = [
    "BaseResponse",
    "TimestampedResponse",
    "IdentifiedResponse",
    "StringIdentifiedResponse",
    "PaginatedResponse",
    "MessageResponse",
    "BulkActionRequest",
    "CountResponse",
    "CategoriesResponse",
    "SubcategoriesResponse",
]
