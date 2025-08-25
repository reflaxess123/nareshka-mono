"""Базовые исключения с structured error responses"""

from typing import Any, Dict, Optional, Union

from fastapi import status

# Avoid circular import - logger will be set up later if needed
logger = None


class BaseAppException(Exception):
    """Базовое исключение для приложения"""

    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.user_message = user_message or "Internal server error"

        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь для JSON response"""
        return {
            "error": self.error_code,
            "message": self.user_message,
            "details": self.details,
            "correlation_id": None,  # Будет добавлено в exception handler
            "timestamp": None,  # Будет добавлено в exception handler
        }


class ValidationException(BaseAppException):
    """Исключение для ошибок валидации"""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.field = field
        self.value = value

        error_details = details or {}
        if field:
            error_details["field"] = field
        if value is not None:
            error_details["value"] = str(value)

        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=error_details,
            user_message=message,
        )


class AuthenticationException(BaseAppException):
    """Исключение для ошибок аутентификации"""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="AUTH_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
            user_message="Authentication required",
        )


class AuthorizationException(BaseAppException):
    """Исключение для ошибок авторизации"""

    def __init__(
        self,
        message: str = "Access denied",
        required_role: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if required_role:
            error_details["required_role"] = required_role

        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=status.HTTP_403_FORBIDDEN,
            details=error_details,
            user_message="Access denied",
        )


class ResourceNotFoundException(BaseAppException):
    """Исключение для ресурсов не найдено"""

    def __init__(
        self,
        resource_type: str,
        resource_id: Optional[Union[str, int]] = None,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        error_details["resource_type"] = resource_type
        if resource_id:
            error_details["resource_id"] = str(resource_id)

        if not message:
            message = f"{resource_type} not found"
            if resource_id:
                message += f" with id: {resource_id}"

        super().__init__(
            message=message,
            error_code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=error_details,
            user_message=message,
        )


class ResourceConflictException(BaseAppException):
    """Исключение для конфликтов ресурсов"""

    def __init__(
        self,
        resource_type: str,
        conflict_field: Optional[str] = None,
        conflict_value: Optional[Any] = None,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        error_details["resource_type"] = resource_type
        if conflict_field:
            error_details["conflict_field"] = conflict_field
        if conflict_value:
            error_details["conflict_value"] = str(conflict_value)

        if not message:
            message = f"{resource_type} already exists"
            if conflict_field:
                message += f" with {conflict_field}: {conflict_value}"

        super().__init__(
            message=message,
            error_code="RESOURCE_CONFLICT",
            status_code=status.HTTP_409_CONFLICT,
            details=error_details,
            user_message=message,
        )


class BusinessLogicException(BaseAppException):
    """Исключение для бизнес-логики"""

    def __init__(
        self,
        message: str,
        business_rule: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if business_rule:
            error_details["business_rule"] = business_rule

        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=error_details,
            user_message=message,
        )


class ExternalServiceException(BaseAppException):
    """Исключение для внешних сервисов"""

    def __init__(
        self,
        service_name: str,
        message: str = "External service error",
        service_status: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        error_details["service_name"] = service_name
        if service_status:
            error_details["service_status"] = service_status

        super().__init__(
            message=f"{service_name}: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=error_details,
            user_message="External service temporarily unavailable",
        )


class DatabaseException(BaseAppException):
    """Исключение для ошибок базы данных"""

    def __init__(
        self,
        message: str = "Database error",
        operation: Optional[str] = None,
        table: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if operation:
            error_details["operation"] = operation
        if table:
            error_details["table"] = table

        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details,
            user_message="Database operation failed",
        )


class ConfigurationException(BaseAppException):
    """Исключение для ошибок конфигурации"""

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if config_key:
            error_details["config_key"] = config_key

        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details,
            user_message="Service configuration error",
        )


class RateLimitException(BaseAppException):
    """Исключение для rate limiting"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit: Optional[str] = None,
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if limit:
            error_details["limit"] = limit
        if retry_after:
            error_details["retry_after"] = retry_after

        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=error_details,
            user_message="Too many requests. Please try again later.",
        )


class CodeExecutionException(BaseAppException):
    """Исключение для выполнения кода"""

    def __init__(
        self,
        message: str = "Code execution failed",
        language: Optional[str] = None,
        exit_code: Optional[int] = None,
        stderr: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if language:
            error_details["language"] = language
        if exit_code is not None:
            error_details["exit_code"] = exit_code
        if stderr:
            error_details["stderr"] = stderr

        super().__init__(
            message=message,
            error_code="CODE_EXECUTION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=error_details,
            user_message="Code execution failed",
        )


# Функции для быстрого создания исключений
def validation_error(
    message: str, field: str = None, value: Any = None
) -> ValidationException:
    """Создать ошибку валидации"""
    return ValidationException(message, field, value)


def not_found(
    resource_type: str, resource_id: Union[str, int] = None
) -> ResourceNotFoundException:
    """Создать ошибку 'не найдено'"""
    return ResourceNotFoundException(resource_type, resource_id)


def unauthorized(message: str = "Authentication required") -> AuthenticationException:
    """Создать ошибку аутентификации"""
    return AuthenticationException(message)


def forbidden(
    message: str = "Access denied", required_role: str = None
) -> AuthorizationException:
    """Создать ошибку авторизации"""
    return AuthorizationException(message, required_role)


def conflict(
    resource_type: str, field: str = None, value: Any = None
) -> ResourceConflictException:
    """Создать ошибку конфликта"""
    return ResourceConflictException(resource_type, field, value)


def business_error(message: str, rule: str = None) -> BusinessLogicException:
    """Создать ошибку бизнес-логики"""
    return BusinessLogicException(message, rule)


def external_service_error(
    service: str, message: str = "Service unavailable"
) -> ExternalServiceException:
    """Создать ошибку внешнего сервиса"""
    return ExternalServiceException(service, message)


def database_error(
    message: str = "Database error", operation: str = None, table: str = None
) -> DatabaseException:
    """Создать ошибку базы данных"""
    return DatabaseException(message, operation, table)


# === Алиасы для совместимости ===
ValidationError = ValidationException
AuthenticationError = AuthenticationException
AuthorizationError = AuthorizationException
NotFoundError = ResourceNotFoundException
ConflictError = ResourceConflictException

# Экспорт всех исключений
__all__ = [
    "BaseAppException",
    "ValidationException",
    "AuthenticationException",
    "AuthorizationException",
    "ResourceNotFoundException",
    "ResourceConflictException",
    "BusinessLogicException",
    "ExternalServiceException",
    "DatabaseException",
    "ConfigurationException",
    "RateLimitException",
    "CodeExecutionException",
    # Алиасы
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ConflictError",
    # Функции
    "validation_error",
    "not_found",
    "unauthorized",
    "forbidden",
    "conflict",
    "business_error",
    "external_service_error",
    "database_error",
]
