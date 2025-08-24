# Shared infrastructure exports for feature modules

# Database components
from .database import (
    Base,
    SessionLocal,
    engine,
    get_db,
    get_session,
)

# Common types
from .types import (
    # Base types
    ID,
    BaseCreateRequest,
    BaseEntity,
    BaseResponse,
    BaseUpdateRequest,
    ContentType,
    Difficulty,
    EntityStatus,
    # Common models
    ErrorDetail,
    # Type aliases
    JsonDict,
    ProgrammingLanguage,
    Result,
    StringDict,
    TaskStatus,
    # Enums
    UserRole,
)

# Shared entities
# from .entities import (
#     User,
#     ContentBlock,
#     ContentFile,
# )
# Utility functions
from .utils import (
    ApiResponse,
    PaginatedResponse,
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
    # Types
    "ID",
    "BaseResponse",
    "BaseEntity",
    "BaseCreateRequest",
    "BaseUpdateRequest",
    "UserRole",
    "EntityStatus",
    "TaskStatus",
    "ContentType",
    "Difficulty",
    "ProgrammingLanguage",
    "ErrorDetail",
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
