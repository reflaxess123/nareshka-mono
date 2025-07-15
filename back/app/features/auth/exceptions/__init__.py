"""
Исключения auth модуля
"""

from .auth_exceptions import (
    # Аутентификация
    InvalidCredentialsError,
    UserNotFoundError,
    AccountDeactivatedError,
    
    # Регистрация
    EmailAlreadyExistsError,
    UsernameAlreadyExistsError,
    
    # Валидация
    WeakPasswordError,
    InvalidEmailError,
    InvalidUsernameError,
    
    # Токены
    TokenError,
    InvalidTokenError,
    TokenExpiredError,
    TokenNotProvidedError,
    
    # Авторизация
    InsufficientPermissionsError,
    AdminAccessRequiredError,
    
    # Сброс пароля
    PasswordResetError,
    InvalidResetTokenError,
    ResetTokenExpiredError,
    
    # Профиль
    ProfileUpdateError,
    ProfileNotFoundError
)

__all__ = [
    # Аутентификация
    "InvalidCredentialsError",
    "UserNotFoundError", 
    "AccountDeactivatedError",
    
    # Регистрация
    "EmailAlreadyExistsError",
    "UsernameAlreadyExistsError",
    
    # Валидация
    "WeakPasswordError",
    "InvalidEmailError",
    "InvalidUsernameError",
    
    # Токены
    "TokenError",
    "InvalidTokenError",
    "TokenExpiredError",
    "TokenNotProvidedError",
    
    # Авторизация
    "InsufficientPermissionsError",
    "AdminAccessRequiredError",
    
    # Сброс пароля
    "PasswordResetError",
    "InvalidResetTokenError",
    "ResetTokenExpiredError",
    
    # Профиль
    "ProfileUpdateError",
    "ProfileNotFoundError"
] 



