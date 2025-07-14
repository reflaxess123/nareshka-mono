# Shared infrastructure exports for feature modules

# Database components
from .database import (
    get_session,
    get_db,
    Base,
    engine,
    SessionLocal,
)

# Shared entities
# from .entities import (
#     User,
#     ContentBlock,
#     ContentFile,
# )

# Utility functions
from .utils import (
    # Validation
    ValidationError,
    ValidationResult,
    validate_email_format,
    validate_password_strength,
    validate_field,
    
    # HTTP utilities
    PaginationParams,
    PaginatedResponse,
    ApiResponse,
    RequestContext,
    extract_pagination,
    extract_filters,
    create_success_response,
    create_error_response,
    create_paginated_response,
    
    # Common status codes
    StatusCodes
)

# Common types
from .types import (
    # Base types
    ID,
    BaseResponse,
    BaseEntity,
    BaseCreateRequest,
    BaseUpdateRequest,
    
    # Enums
    UserRole,
    EntityStatus,
    TaskStatus,
    ContentType,
    Difficulty,
    ProgrammingLanguage,
    
    # Common models
    ErrorDetail,
    Result,
    
    # Type aliases
    JsonDict,
    StringDict
)

# Exception handling (temporarily import from base module)
try:
    from .exceptions.base import (
        DatabaseException as DatabaseError,
        ResourceNotFoundException as EntityNotFoundError,
        ResourceConflictException as DuplicateEntityError,
        ValidationException as SharedValidationError,
        not_found as create_http_exception,
        validation_error as create_validation_exception
    )
except ImportError:
    # Fallback if exceptions module structure is different
    DatabaseError = Exception
    EntityNotFoundError = Exception 
    DuplicateEntityError = Exception
    SharedValidationError = Exception
    def create_http_exception(*args, **kwargs): return Exception()
    def create_validation_exception(*args, **kwargs): return Exception()

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



