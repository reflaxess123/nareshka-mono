"""Base schema classes for API responses and requests"""

from datetime import datetime
from typing import Any, Dict, Generic, List, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

# Type variables for Generic classes
T = TypeVar("T")
ItemT = TypeVar("ItemT", bound=BaseModel)


class BaseResponse(BaseModel):
    """Base response DTO with common settings"""

    class Config:
        from_attributes = True


class TimestampedResponse(BaseResponse):
    """Response DTO with timestamps"""

    createdAt: datetime
    updatedAt: datetime


class IdentifiedResponse(TimestampedResponse):
    """Response DTO with ID and timestamps"""

    id: int


class StringIdentifiedResponse(TimestampedResponse):
    """Response DTO with string ID and timestamps"""

    id: str


class PaginationInfo(BaseModel):
    """Pagination information"""

    page: int
    limit: int
    total: int
    totalPages: int

    @classmethod
    def create(cls, page: int, limit: int, total: int) -> "PaginationInfo":
        """Create pagination info"""
        total_pages = (total + limit - 1) // limit if total > 0 else 0
        return cls(page=page, limit=limit, total=total, totalPages=total_pages)


class PaginatedResponse(GenericModel, Generic[ItemT]):
    """Generic paginated response"""

    items: List[ItemT]
    pagination: PaginationInfo

    @classmethod
    def create(
        cls, items: List[ItemT], page: int, limit: int, total: int
    ) -> "PaginatedResponse[ItemT]":
        """Create paginated response"""
        pagination = PaginationInfo.create(page, limit, total)
        return cls(items=items, pagination=pagination)


class CategoriesResponse(BaseModel):
    """Response with categories list"""
    
    categories: List[str]

    @classmethod
    def create(cls, categories: List[str]) -> "CategoriesResponse":
        """Create categories response"""
        return cls(categories=categories)


class SubcategoriesResponse(BaseModel):
    """Response with subcategories list"""
    
    subcategories: List[str]

    @classmethod
    def create(cls, subcategories: List[str]) -> "SubcategoriesResponse":
        """Create subcategories response"""
        return cls(subcategories=subcategories)


class CountResponse(BaseModel):
    """Response with count"""

    count: int


class MessageResponse(BaseModel):
    """Response with message"""

    message: str

    @classmethod
    def success(
        cls, message: str = "Operation completed successfully"
    ) -> "MessageResponse":
        """Create success response"""
        return cls(message=message)

    @classmethod
    def error(cls, message: str) -> "MessageResponse":
        """Create error response"""
        return cls(message=message)


class BulkActionRequest(BaseModel):
    """Request for bulk actions"""

    ids: List[int]

    def validate_ids(self) -> None:
        """Validate IDs list"""
        if not self.ids:
            raise ValueError("IDs list cannot be empty")
        if len(self.ids) > 1000:  # Protection against too large requests
            raise ValueError("Too many IDs (max 1000)")