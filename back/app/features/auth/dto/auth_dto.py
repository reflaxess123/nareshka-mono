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
    role: UserRole
    totalTasksSolved: int
    lastActivityDate: Optional[datetime]

    class Config:
        from_attributes = True  # Для работы с SQLAlchemy моделями


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


class TokenData(BaseModel):
    """Данные токена"""

    email: str
    user_id: int
