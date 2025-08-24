"""
Исключения auth модуля
"""

from .auth_exceptions import (
    AccountDeactivatedError,
    AdminAccessRequiredError,
    # Регистрация
    EmailAlreadyExistsError,
    # Авторизация
    InsufficientPermissionsError,
    # Аутентификация
    InvalidCredentialsError,
    InvalidEmailError,
    InvalidResetTokenError,
    InvalidTokenError,
    InvalidUsernameError,
    # Сброс пароля
    PasswordResetError,
    ProfileNotFoundError,
    # Профиль
    ProfileUpdateError,
    ResetTokenExpiredError,
    # Токены
    TokenError,
    TokenExpiredError,
    TokenNotProvidedError,
    UsernameAlreadyExistsError,
    UserNotFoundError,
    # Валидация
    WeakPasswordError,
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
    "ProfileNotFoundError",
]
