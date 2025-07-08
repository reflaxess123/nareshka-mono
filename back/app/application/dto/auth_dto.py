"""DTO для аутентификации"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

from ...infrastructure.models.enums import UserRole
from .base_dto import IdentifiedResponse, MessageResponse


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