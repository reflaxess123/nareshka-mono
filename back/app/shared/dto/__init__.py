"""Shared DTOs - общие типы данных для всего приложения"""

from .base_dto import (
    BaseResponse,
    BulkActionRequest,
    CountResponse,
    CreateRequest,
    IdentifiedResponse,
    MessageResponse,
    PaginatedResponse,
    StringIdentifiedResponse,
    TimestampedResponse,
    UpdateRequest,
)

__all__ = [
    "BaseResponse",
    "TimestampedResponse",
    "IdentifiedResponse",
    "StringIdentifiedResponse",
    "PaginatedResponse",
    "MessageResponse",
    "CreateRequest",
    "UpdateRequest",
    "BulkActionRequest",
    "CountResponse",
]
