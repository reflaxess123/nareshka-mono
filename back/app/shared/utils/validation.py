"""
Validation utilities for use across features.
Provides common validation patterns and custom validators.
"""

import re
from typing import Any, Optional, List, Dict, Union, Callable
from datetime import datetime, date
from email_validator import validate_email, EmailNotValidError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Common regex patterns
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
PHONE_PATTERN = re.compile(r'^\+?1?[0-9]{10,15}$')
USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]{3,20}$')
PASSWORD_PATTERN = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$')
UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)


class ValidationError(Exception):
    """Custom validation error."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(message)


class ValidationResult:
    """Result of validation operation."""
    
    def __init__(self, is_valid: bool = True, errors: Optional[List[str]] = None):
        self.is_valid = is_valid
        self.errors = errors or []
    
    def add_error(self, error: str):
        """Add validation error."""
        self.errors.append(error)
        self.is_valid = False


def validate_email_format(email: str) -> bool:
    """Validate email format using robust validation."""
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


def validate_phone_format(phone: str) -> bool:
    """Validate phone number format."""
    return bool(PHONE_PATTERN.match(phone.replace(' ', '').replace('-', '')))


def validate_username_format(username: str) -> bool:
    """Validate username format."""
    return bool(USERNAME_PATTERN.match(username))


def validate_password_strength(password: str) -> ValidationResult:
    """
    Validate password strength.
    Requirements: 8+ chars, uppercase, lowercase, digit.
    """
    result = ValidationResult()
    
    if len(password) < 8:
        result.add_error("Password must be at least 8 characters long")
    
    if not re.search(r'[a-z]', password):
        result.add_error("Password must contain at least one lowercase letter")
    
    if not re.search(r'[A-Z]', password):
        result.add_error("Password must contain at least one uppercase letter")
    
    if not re.search(r'\d', password):
        result.add_error("Password must contain at least one digit")
    
    return result


def validate_uuid_format(uuid_str: str) -> bool:
    """Validate UUID format."""
    return bool(UUID_PATTERN.match(uuid_str))


def validate_date_format(date_str: str, format_str: str = "%Y-%m-%d") -> bool:
    """Validate date string format."""
    try:
        datetime.strptime(date_str, format_str)
        return True
    except ValueError:
        return False


def validate_datetime_format(datetime_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> bool:
    """Validate datetime string format."""
    try:
        datetime.strptime(datetime_str, format_str)
        return True
    except ValueError:
        return False


def validate_json_keys(data: Dict[str, Any], required_keys: List[str], optional_keys: Optional[List[str]] = None) -> ValidationResult:
    """Validate that JSON data contains required keys and no unexpected keys."""
    result = ValidationResult()
    optional_keys = optional_keys or []
    allowed_keys = set(required_keys + optional_keys)
    
    # Check required keys
    for key in required_keys:
        if key not in data:
            result.add_error(f"Missing required key: {key}")
    
    # Check for unexpected keys
    for key in data.keys():
        if key not in allowed_keys:
            result.add_error(f"Unexpected key: {key}")
    
    return result


def validate_string_length(value: str, min_length: int = 0, max_length: Optional[int] = None, field_name: str = "field") -> ValidationResult:
    """Validate string length constraints."""
    result = ValidationResult()
    
    if len(value) < min_length:
        result.add_error(f"{field_name} must be at least {min_length} characters long")
    
    if max_length and len(value) > max_length:
        result.add_error(f"{field_name} must be no more than {max_length} characters long")
    
    return result


def validate_numeric_range(value: Union[int, float], min_value: Optional[Union[int, float]] = None, 
                          max_value: Optional[Union[int, float]] = None, field_name: str = "field") -> ValidationResult:
    """Validate numeric value within range."""
    result = ValidationResult()
    
    if min_value is not None and value < min_value:
        result.add_error(f"{field_name} must be at least {min_value}")
    
    if max_value is not None and value > max_value:
        result.add_error(f"{field_name} must be no more than {max_value}")
    
    return result


def validate_choice(value: Any, choices: List[Any], field_name: str = "field") -> ValidationResult:
    """Validate that value is in allowed choices."""
    result = ValidationResult()
    
    if value not in choices:
        result.add_error(f"{field_name} must be one of: {', '.join(map(str, choices))}")
    
    return result


def sanitize_string(value: str, max_length: Optional[int] = None, strip: bool = True, 
                   remove_html: bool = False) -> str:
    """Sanitize string input."""
    if strip:
        value = value.strip()
    
    if remove_html:
        # Basic HTML tag removal
        value = re.sub(r'<[^>]+>', '', value)
    
    if max_length:
        value = value[:max_length]
    
    return value


def validate_file_type(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file type by extension."""
    if not filename:
        return False
    
    extension = filename.lower().split('.')[-1]
    return extension in [ext.lower().lstrip('.') for ext in allowed_extensions]


def validate_file_size(size_bytes: int, max_size_mb: int) -> bool:
    """Validate file size."""
    max_size_bytes = max_size_mb * 1024 * 1024
    return size_bytes <= max_size_bytes


class FieldValidator:
    """Chainable field validator for complex validation scenarios."""
    
    def __init__(self, field_name: str, value: Any):
        self.field_name = field_name
        self.value = value
        self.errors = []
    
    def required(self) -> 'FieldValidator':
        """Mark field as required."""
        if self.value is None or self.value == '':
            self.errors.append(f"{self.field_name} is required")
        return self
    
    def email(self) -> 'FieldValidator':
        """Validate email format."""
        if self.value and not validate_email_format(self.value):
            self.errors.append(f"{self.field_name} must be a valid email")
        return self
    
    def length(self, min_length: int = 0, max_length: Optional[int] = None) -> 'FieldValidator':
        """Validate string length."""
        if self.value:
            result = validate_string_length(self.value, min_length, max_length, self.field_name)
            self.errors.extend(result.errors)
        return self
    
    def choice(self, choices: List[Any]) -> 'FieldValidator':
        """Validate choice from list."""
        if self.value:
            result = validate_choice(self.value, choices, self.field_name)
            self.errors.extend(result.errors)
        return self
    
    def custom(self, validator_func: Callable[[Any], bool], error_message: str) -> 'FieldValidator':
        """Apply custom validator function."""
        if self.value and not validator_func(self.value):
            self.errors.append(error_message)
        return self
    
    def get_result(self) -> ValidationResult:
        """Get validation result."""
        return ValidationResult(is_valid=len(self.errors) == 0, errors=self.errors)


def validate_field(field_name: str, value: Any) -> FieldValidator:
    """Start field validation chain."""
    return FieldValidator(field_name, value)


# Common validation combinations
def validate_user_registration_data(data: Dict[str, Any]) -> ValidationResult:
    """Validate user registration data."""
    result = ValidationResult()
    
    # Validate required fields
    key_result = validate_json_keys(data, ['username', 'email', 'password'])
    result.errors.extend(key_result.errors)
    
    if not key_result.is_valid:
        return result
    
    # Validate username
    username_result = validate_field('username', data.get('username')).required().length(3, 20).custom(
        validate_username_format, "Username must contain only letters, numbers, and underscores"
    ).get_result()
    result.errors.extend(username_result.errors)
    
    # Validate email
    email_result = validate_field('email', data.get('email')).required().email().get_result()
    result.errors.extend(email_result.errors)
    
    # Validate password
    password_result = validate_password_strength(data.get('password', ''))
    result.errors.extend(password_result.errors)
    
    result.is_valid = len(result.errors) == 0
    return result


def log_validation_error(field: str, value: Any, error: str, user_id: Optional[str] = None):
    """Log validation error with context."""
    logger.warning("Validation error", extra={
        "field": field,
        "error": error,
        "user_id": user_id,
        "value_type": type(value).__name__
    }) 


