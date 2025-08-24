"""
HTTP utilities for API responses, pagination, and common request handling.
"""

from dataclasses import dataclass
from typing import Any, Dict, Generic, List, Optional, TypeVar

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


@dataclass
class PaginationParams:
    """Standard pagination parameters."""

    page: int = 1
    size: int = 20
    skip: int = 0

    def __post_init__(self):
        self.page = max(self.page, 1)
        if self.size < 1:
            self.size = 20
        self.size = min(self.size, 100)
        self.skip = (self.page - 1) * self.size


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response format."""

    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool

    @classmethod
    def create(
        cls, items: List[T], total: int, pagination: PaginationParams
    ) -> "PaginatedResponse[T]":
        """Create paginated response from items and total count."""
        pages = (total + pagination.size - 1) // pagination.size

        return cls(
            items=items,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=pages,
            has_next=pagination.page < pages,
            has_prev=pagination.page > 1,
        )


class ApiResponse(BaseModel):
    """Standard API response format."""

    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
    meta: Optional[Dict[str, Any]] = None

    @classmethod
    def success_response(
        cls,
        data: Any = None,
        message: str = "Success",
        meta: Optional[Dict[str, Any]] = None,
    ) -> "ApiResponse":
        """Create successful response."""
        return cls(success=True, message=message, data=data, meta=meta)

    @classmethod
    def error_response(
        cls,
        message: str = "Error",
        errors: Optional[List[str]] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> "ApiResponse":
        """Create error response."""
        return cls(success=False, message=message, errors=errors or [], meta=meta)


def extract_pagination(
    request: Request, default_size: int = 20, max_size: int = 100
) -> PaginationParams:
    """Extract pagination parameters from request."""
    try:
        page = int(request.query_params.get("page", 1))
        size = int(request.query_params.get("size", default_size))

        return PaginationParams(page=page, size=min(size, max_size))

    except (ValueError, TypeError):
        logger.warning(
            "Invalid pagination parameters",
            extra={
                "page": request.query_params.get("page"),
                "size": request.query_params.get("size"),
            },
        )
        return PaginationParams(page=1, size=default_size)


def extract_filters(request: Request, allowed_filters: List[str]) -> Dict[str, Any]:
    """Extract filter parameters from request query."""
    filters = {}

    for filter_name in allowed_filters:
        value = request.query_params.get(filter_name)
        if value is not None:
            # Try to convert to appropriate type
            if value.lower() in ["true", "false"]:
                filters[filter_name] = value.lower() == "true"
            elif value.isdigit():
                filters[filter_name] = int(value)
            else:
                filters[filter_name] = value

    logger.debug(
        "Extracted filters",
        extra={"filters": filters, "allowed_filters": allowed_filters},
    )

    return filters


def extract_sort_params(
    request: Request, allowed_fields: List[str], default_field: str = "id"
) -> Dict[str, str]:
    """Extract sort parameters from request."""
    sort_by = request.query_params.get("sort_by", default_field)
    sort_order = request.query_params.get("sort_order", "asc").lower()

    # Validate sort field
    if sort_by not in allowed_fields:
        sort_by = default_field

    # Validate sort order
    if sort_order not in ["asc", "desc"]:
        sort_order = "asc"

    return {"sort_by": sort_by, "sort_order": sort_order}


def get_client_ip(request: Request) -> str:
    """Get client IP address from request."""
    # Check for forwarded headers (common in load balancers)
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    forwarded = request.headers.get("x-forwarded")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip

    # Fallback to client host
    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    """Get user agent from request."""
    return request.headers.get("user-agent", "unknown")


def log_request(
    request: Request,
    user_id: Optional[str] = None,
    extra_data: Optional[Dict[str, Any]] = None,
):
    """Log HTTP request with context."""
    log_data = {
        "method": request.method,
        "url": str(request.url),
        "client_ip": get_client_ip(request),
        "user_agent": get_user_agent(request),
        "user_id": user_id,
    }

    if extra_data:
        log_data.update(extra_data)

    logger.info("HTTP request", extra=log_data)


def create_error_response(
    status_code: int,
    message: str,
    errors: Optional[List[str]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> JSONResponse:
    """Create standardized error response."""
    response_data = ApiResponse.error_response(message=message, errors=errors)

    return JSONResponse(
        status_code=status_code, content=response_data.dict(), headers=headers
    )


def create_success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    """Create standardized success response."""
    response_data = ApiResponse.success_response(data=data, message=message, meta=meta)

    return JSONResponse(
        status_code=status_code, content=response_data.dict(), headers=headers
    )


def create_paginated_response(
    items: List[Any],
    total: int,
    pagination: PaginationParams,
    message: str = "Success",
    status_code: int = 200,
) -> JSONResponse:
    """Create paginated response."""
    paginated_data = PaginatedResponse.create(items, total, pagination)
    response_data = ApiResponse.success_response(
        data=paginated_data.dict(), message=message
    )

    return JSONResponse(status_code=status_code, content=response_data.dict())


def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with consistent format."""
    logger.warning(
        "HTTP exception",
        extra={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "url": str(request.url),
            "method": request.method,
        },
    )

    return create_error_response(
        status_code=exc.status_code,
        message=exc.detail if isinstance(exc.detail, str) else "HTTP Error",
        errors=[exc.detail] if isinstance(exc.detail, str) else [],
    )


def validate_content_type(request: Request, expected_types: List[str] = None) -> bool:
    """Validate request content type."""
    if expected_types is None:
        expected_types = ["application/json"]

    content_type = request.headers.get("content-type", "").lower()

    for expected in expected_types:
        if expected.lower() in content_type:
            return True

    return False


def extract_bearer_token(request: Request) -> Optional[str]:
    """Extract bearer token from Authorization header."""
    auth_header = request.headers.get("authorization")
    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    return parts[1]


class RequestContext:
    """Request context helper for collecting request information."""

    def __init__(self, request: Request):
        self.request = request
        self.client_ip = get_client_ip(request)
        self.user_agent = get_user_agent(request)
        self.method = request.method
        self.url = str(request.url)
        self.headers = dict(request.headers)
        self.query_params = dict(request.query_params)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "client_ip": self.client_ip,
            "user_agent": self.user_agent,
            "method": self.method,
            "url": self.url,
            "query_params": self.query_params,
        }

    def log_context(
        self, level: str = "info", message: str = "Request context", **extra
    ):
        """Log request context."""
        log_data = self.to_dict()
        log_data.update(extra)

        logger.log(level.upper(), message, extra=log_data)


# HTTP status code helpers
class StatusCodes:
    """Common HTTP status codes."""

    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500
