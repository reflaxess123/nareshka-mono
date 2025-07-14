"""
Зависимости для аутентификации и авторизации
"""

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.shared.types.common import UserRole
from app.shared.dependencies import get_database_manager
from app.shared.database.base import DatabaseManager

from ..models.user import User
from ..repositories.user_repository import UserRepository
from ..services.user_service import UserService
from ..exceptions.auth_exceptions import (
    InvalidTokenError,
    TokenNotProvidedError,
    InsufficientPermissionsError,
    AdminAccessRequiredError
)

# Настройка HTTP Bearer токена
security = HTTPBearer(auto_error=False)

# === Фабрики зависимостей ===

def get_user_repository() -> UserRepository:
    """Получение репозитория пользователей"""
    return UserRepository()

def get_user_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)]
) -> UserService:
    """Получение сервиса пользователей"""
    return UserService(user_repository)

# === Аутентификация ===

async def get_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)]
) -> str:
    """Извлечение токена из заголовка Authorization"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не предоставлен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

async def get_current_user(
    token: Annotated[str, Depends(get_token)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> User:
    """Получение текущего пользователя по токену"""
    try:
        return await user_service.get_current_user(token)
    except (InvalidTokenError, Exception) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Получение текущего активного пользователя"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неактивный пользователь"
        )
    return current_user

# === Авторизация по ролям ===

def require_role(required_role: UserRole):
    """Декоратор для проверки роли пользователя"""
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_active_user)]
    ) -> User:
        if not current_user.has_permission(required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав доступа"
            )
        return current_user
    return role_checker

# Готовые зависимости для ролей
require_admin = require_role(UserRole.ADMIN)
require_user = require_role(UserRole.USER)

async def get_current_admin(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """Получение текущего пользователя с правами администратора"""
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора"
        )
    return current_user

# === Опциональная аутентификация ===

async def get_optional_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)]
) -> str | None:
    """Извлечение токена (опционально)"""
    if not credentials:
        return None
    return credentials.credentials

async def get_optional_current_user(
    token: Annotated[str | None, Depends(get_optional_token)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> User | None:
    """Получение текущего пользователя (опционально)"""
    if not token:
        return None
    
    try:
        return await user_service.get_current_user(token)
    except Exception:
        return None

# === Типы для аннотаций ===

CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
CurrentAdmin = Annotated[User, Depends(get_current_admin)]
OptionalUser = Annotated[User | None, Depends(get_optional_current_user)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)] 


