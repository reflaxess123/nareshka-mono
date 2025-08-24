"""DTO для аутентификации"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.shared.models.enums import UserRole


class IdentifiedResponse(BaseModel):
    """Базовый ответ с идентификатором"""

    id: int
    createdAt: datetime
    updatedAt: datetime


class MessageResponse(BaseModel):
    """Базовый ответ с сообщением"""

    message: str


class LoginRequest(BaseModel):
    """Запрос на вход"""

    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Запрос на регистрацию"""

    email: EmailStr
    password: str


class UserResponse(IdentifiedResponse):
    """Ответ с данными пользователя"""

    email: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    display_name: str
    role: UserRole
    is_active: bool = True
    is_verified: bool = True
    totalTasksSolved: int
    lastActivityDate: Optional[datetime]

    @classmethod
    def from_user(cls, user) -> "UserResponse":
        """Create response from User model."""
        return cls(
            id=user.id,
            email=user.email,
            username=user.username if hasattr(user, 'username') else None,
            first_name=user.first_name if hasattr(user, 'first_name') else None,
            last_name=user.last_name if hasattr(user, 'last_name') else None,
            full_name=user.full_name if hasattr(user, 'full_name') else None,
            display_name=user.display_name if hasattr(user, 'display_name') else user.email.split('@')[0],
            role=user.role,
            is_active=user.is_active if hasattr(user, 'is_active') else True,
            is_verified=user.is_verified if hasattr(user, 'is_verified') else True,
            totalTasksSolved=user.totalTasksSolved,
            lastActivityDate=user.lastActivityDate,
            createdAt=user.createdAt,
            updatedAt=user.updatedAt if hasattr(user, 'updatedAt') else user.createdAt,
        )

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Ответ на успешный вход"""

    access_token: str
    token_type: str
    user: UserResponse
    session_id: Optional[str] = None


class RegisterResponse(BaseModel):
    """Ответ на успешную регистрацию"""

    user: UserResponse
    message: str


class LogoutResponse(MessageResponse):
    """Ответ на выход"""

    pass
