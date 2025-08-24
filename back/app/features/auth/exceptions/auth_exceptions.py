"""
Исключения для auth модуля
"""

from app.shared.exceptions.base import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)

# === Исключения аутентификации ===


class InvalidCredentialsError(AuthenticationError):
    """Неверные учетные данные"""

    pass


class UserNotFoundError(NotFoundError):
    """Пользователь не найден"""

    pass


class AccountDeactivatedError(AuthenticationError):
    """Аккаунт деактивирован"""

    pass


# === Исключения регистрации ===


class EmailAlreadyExistsError(ConflictError):
    """Email уже используется"""

    pass


class UsernameAlreadyExistsError(ConflictError):
    """Username уже используется"""

    pass


# === Исключения валидации ===


class WeakPasswordError(ValidationError):
    """Слабый пароль"""

    pass


class InvalidEmailError(ValidationError):
    """Некорректный email"""

    pass


class InvalidUsernameError(ValidationError):
    """Некорректный username"""

    pass


# === Исключения токенов ===


class TokenError(AuthenticationError):
    """Базовое исключение для ошибок токенов"""

    pass


class InvalidTokenError(TokenError):
    """Некорректный токен"""

    pass


class TokenExpiredError(TokenError):
    """Токен просрочен"""

    pass


class TokenNotProvidedError(TokenError):
    """Токен не предоставлен"""

    pass


# === Исключения авторизации ===


class InsufficientPermissionsError(AuthorizationError):
    """Недостаточно прав доступа"""

    pass


class AdminAccessRequiredError(AuthorizationError):
    """Требуется доступ администратора"""

    pass


# === Исключения сброса пароля ===


class PasswordResetError(ValidationError):
    """Базовое исключение для ошибок сброса пароля"""

    pass


class InvalidResetTokenError(PasswordResetError):
    """Некорректный токен сброса пароля"""

    pass


class ResetTokenExpiredError(PasswordResetError):
    """Токен сброса пароля просрочен"""

    pass


# === Исключения профиля ===


class ProfileUpdateError(ValidationError):
    """Ошибка обновления профиля"""

    pass


class ProfileNotFoundError(NotFoundError):
    """Профиль не найден"""

    pass
