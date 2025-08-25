# Shared infrastructure exports for feature modules

# Database components
from .database import (
    Base,
    SessionLocal,
    engine,
    get_db,
    get_session,
)

# Common schemas
from .schemas.base import (
    BaseResponse,
    PaginatedResponse as SchemaPaginatedResponse,
)

# Common types and enums from models
from .models.enums import (
    UserRole,
    CardState,
    CodeLanguage,
    ExecutionStatus,
    ProgressStatus,
)

# Type aliases
ID = str
JsonDict = dict
StringDict = dict[str, str]
Result = tuple[bool, str]

from .utils import (
    ApiResponse,
    # HTTP utilities
    PaginationParams,
    RequestContext,
    # Common status codes
    StatusCodes,
    # Validation
    ValidationError,
    ValidationResult,
    create_error_response,
    create_paginated_response,
    create_success_response,
    extract_filters,
    extract_pagination,
    validate_email_format,
    validate_field,
    validate_password_strength,
)

# Re-export PaginatedResponse from schemas
from .schemas.base import PaginatedResponse

# Exception handling (temporarily import from base module)
try:
    from .exceptions.base import (
        DatabaseException as DatabaseError,
        ResourceConflictException as DuplicateEntityError,
        ResourceNotFoundException as EntityNotFoundError,
        ValidationException as SharedValidationError,
        not_found as create_http_exception,
        validation_error as create_validation_exception,
    )
except ImportError:
    # Fallback if exceptions module structure is different
    DatabaseError = Exception
    EntityNotFoundError = Exception
    DuplicateEntityError = Exception
    SharedValidationError = Exception

    def create_http_exception(*args, **kwargs):
        return Exception()

    def create_validation_exception(*args, **kwargs):
        return Exception()


__all__ = [
    # Database
    "get_session",
    "get_db",
    "Base",
    "engine",
    "SessionLocal",
    # Utilities
    "ValidationError",
    "ValidationResult",
    "validate_email_format",
    "validate_password_strength",
    "validate_field",
    "PaginationParams",
    "PaginatedResponse",
    "ApiResponse",
    "RequestContext",
    "extract_pagination",
    "extract_filters",
    "create_success_response",
    "create_error_response",
    "create_paginated_response",
    "StatusCodes",
    # Schemas
    "BaseResponse",
    # Enums
    "UserRole",
    "CardState",
    "CodeLanguage",
    "ExecutionStatus",
    "ProgressStatus",
    # Type aliases
    "ID",
    "Result",
    "JsonDict",
    "StringDict",
    # Exceptions
    "DatabaseError",
    "EntityNotFoundError",
    "DuplicateEntityError",
    "SharedValidationError",
    "create_http_exception",
    "create_validation_exception",
]
