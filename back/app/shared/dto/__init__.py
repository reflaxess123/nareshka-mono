"""Shared DTOs - общие типы данных для всего приложения"""

from .base_dto import (
    BaseResponse,
    TimestampedResponse,
    IdentifiedResponse,
    StringIdentifiedResponse,
    PaginatedResponse,
    MessageResponse,
    CreateRequest,
    UpdateRequest,
    BulkActionRequest,
    CountResponse
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
    "CountResponse"
] 


