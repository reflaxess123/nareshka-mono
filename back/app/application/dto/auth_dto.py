"""DTO для авторизации"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

from ...domain.entities.enums import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: "UserResponse"
    session_id: Optional[str] = None  # Для сессионной авторизации


class UserResponse(BaseModel):
    id: int
    email: str
    role: UserRole
    createdAt: datetime
    totalTasksSolved: int
    lastActivityDate: Optional[datetime]

    class Config:
        from_attributes = True


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterResponse(BaseModel):
    user: UserResponse
    message: str


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None 