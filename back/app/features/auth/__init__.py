"""
Auth Feature - Аутентификация и управление пользователями (session-based)

Этот модуль реализует простую session-based аутентификацию:
- Регистрация и вход пользователей
- Session-based авторизация с Redis
- Простые DTO без сложной валидации
"""

from app.shared.models.user_models import User
from .repositories.user_repository import UserRepository
from .repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from .services.auth_service import AuthService
# Router импортируется напрямую в main.py для избежания циклических импортов
from .dto.auth_dto import (
    LoginRequest,
    RegisterRequest,
    LoginResponse,
    RegisterResponse,
    UserResponse,
    LogoutResponse,
    TokenData
)

__all__ = [
    "User",
    "UserRepository", 
    "SQLAlchemyUserRepository",
    "AuthService",
    "LoginRequest",
    "RegisterRequest",
    "LoginResponse", 
    "RegisterResponse",
    "UserResponse",
    "LogoutResponse",
    "TokenData"
] 



