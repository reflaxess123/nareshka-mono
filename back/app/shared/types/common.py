"""
Common type definitions for use across features.
Provides standard types for consistency and type safety.
"""

from typing import Union, Optional, Dict, Any, List, TypeVar, Generic, Protocol
from enum import Enum
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


# Generic types
T = TypeVar('T')
ID = Union[int, str, UUID]

# Base response types
class BaseResponse(BaseModel):
    """Base response model for all API responses."""
    class Config:
        from_attributes = True
        use_enum_values = True


class BaseEntity(BaseModel):
    """Base entity model with common fields."""
    id: Optional[ID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        use_enum_values = True


class BaseCreateRequest(BaseModel):
    """Base model for create requests."""
    pass


class BaseUpdateRequest(BaseModel):
    """Base model for update requests."""
    pass


# Common enum types
class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"
    GUEST = "guest"


class EntityStatus(str, Enum):
    """General entity status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class TaskStatus(str, Enum):
    """Task status enumeration."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ContentType(str, Enum):
    """Content type enumeration."""
    THEORY = "theory"
    PRACTICE = "practice"
    TEST = "test"
    VIDEO = "video"
    EXERCISE = "exercise"


class Difficulty(str, Enum):
    """Difficulty level enumeration."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ProgrammingLanguage(str, Enum):
    """Programming language enumeration."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"


# Validation types
class EmailStr(str):
    """Email string type."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        from app.shared.utils.validation import validate_email_format
        if not validate_email_format(v):
            raise ValueError('Invalid email format')
        return v


# Pagination types
class PaginationMeta(BaseModel):
    """Pagination metadata."""
    page: int = Field(ge=1, description="Current page number")
    size: int = Field(ge=1, le=100, description="Items per page")
    total: int = Field(ge=0, description="Total number of items")
    pages: int = Field(ge=0, description="Total number of pages")
    has_next: bool = Field(description="Has next page")
    has_prev: bool = Field(description="Has previous page")


class SortOrder(str, Enum):
    """Sort order enumeration."""
    ASC = "asc"
    DESC = "desc"


class SortParams(BaseModel):
    """Sort parameters."""
    sort_by: str = Field(default="id", description="Field to sort by")
    sort_order: SortOrder = Field(default=SortOrder.ASC, description="Sort order")


# Error types
class ErrorDetail(BaseModel):
    """Error detail model."""
    code: str = Field(description="Error code")
    message: str = Field(description="Error message")
    field: Optional[str] = Field(None, description="Related field")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class ValidationErrorDetail(ErrorDetail):
    """Validation error detail."""
    code: str = "validation_error"
    field: str = Field(description="Field that failed validation")
    value: Optional[Any] = Field(None, description="Invalid value")


# Common protocols for type hints
class Repository(Protocol[T]):
    """Repository protocol for type hints."""
    def create(self, data: Dict[str, Any]) -> T: ...
    def get_by_id(self, entity_id: ID) -> Optional[T]: ...
    def update(self, entity_id: ID, data: Dict[str, Any]) -> T: ...
    def delete(self, entity_id: ID) -> bool: ...


class Service(Protocol[T]):
    """Service protocol for type hints."""
    def create(self, data: BaseCreateRequest) -> T: ...
    def get_by_id(self, entity_id: ID) -> T: ...
    def update(self, entity_id: ID, data: BaseUpdateRequest) -> T: ...
    def delete(self, entity_id: ID) -> bool: ...


# File handling types
class FileInfo(BaseModel):
    """File information model."""
    filename: str = Field(description="Original filename")
    content_type: str = Field(description="MIME content type")
    size: int = Field(ge=0, description="File size in bytes")
    path: Optional[str] = Field(None, description="Storage path")
    url: Optional[str] = Field(None, description="Access URL")


class ImageInfo(FileInfo):
    """Image file information."""
    width: Optional[int] = Field(None, ge=1, description="Image width")
    height: Optional[int] = Field(None, ge=1, description="Image height")


# Authentication types
class TokenType(str, Enum):
    """Token type enumeration."""
    ACCESS = "access"
    REFRESH = "refresh"
    RESET = "reset"
    VERIFICATION = "verification"


class AuthTokenData(BaseModel):
    """Authentication token data."""
    user_id: str = Field(description="User identifier")
    role: UserRole = Field(description="User role")
    token_type: TokenType = Field(description="Token type")
    expires_at: datetime = Field(description="Token expiration time")


# Progress tracking types
class ProgressStatus(str, Enum):
    """Progress status enumeration."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVIEWED = "reviewed"


class ProgressInfo(BaseModel):
    """Progress information."""
    status: ProgressStatus = Field(description="Progress status")
    completion_percentage: float = Field(ge=0, le=100, description="Completion percentage")
    started_at: Optional[datetime] = Field(None, description="Start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    time_spent: Optional[int] = Field(None, ge=0, description="Time spent in seconds")


# Audit types
class AuditAction(str, Enum):
    """Audit action enumeration."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"
    LOGIN = "login"
    LOGOUT = "logout"


class AuditLog(BaseModel):
    """Audit log entry."""
    action: AuditAction = Field(description="Performed action")
    user_id: Optional[str] = Field(None, description="User who performed action")
    entity_type: str = Field(description="Type of entity affected")
    entity_id: Optional[str] = Field(None, description="ID of affected entity")
    timestamp: datetime = Field(description="Action timestamp")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")


# Configuration types
class EnvironmentType(str, Enum):
    """Environment type enumeration."""
    DEVELOPMENT = "development"
    STAGING = "staging" 
    PRODUCTION = "production"
    TESTING = "testing"


class FeatureFlag(BaseModel):
    """Feature flag configuration."""
    name: str = Field(description="Feature flag name")
    enabled: bool = Field(description="Whether feature is enabled")
    description: Optional[str] = Field(None, description="Feature description")
    environment: Optional[EnvironmentType] = Field(None, description="Target environment")


# Generic result types
class Result(BaseModel, Generic[T]):
    """Generic result wrapper."""
    success: bool = Field(description="Operation success status")
    data: Optional[T] = Field(None, description="Result data")
    error: Optional[ErrorDetail] = Field(None, description="Error details")

    @classmethod
    def success(cls, data: T) -> 'Result[T]':
        """Create successful result."""
        return cls(success=True, data=data)

    @classmethod
    def error(cls, error: ErrorDetail) -> 'Result[T]':
        """Create error result."""
        return cls(success=False, error=error)


# === Validation Helper Functions ===

def validate_not_empty(value: str, field_name: str = "field") -> str:
    """Валидация что строка не пустая"""
    if not value or not value.strip():
        raise ValueError(f"{field_name} не может быть пустым")
    return value.strip()

def validate_positive_int(value: int, field_name: str = "field") -> int:
    """Валидация что число положительное"""
    if value <= 0:
        raise ValueError(f"{field_name} должен быть положительным числом")
    return value


# Utility type aliases
JsonDict = Dict[str, Any]
StringDict = Dict[str, str]
Headers = Dict[str, str]
QueryParams = Dict[str, Any] 


