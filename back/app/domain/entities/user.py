"""Сущность пользователя"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass

from .enums import UserRole


@dataclass
class User:
    """Доменная сущность пользователя"""
    id: Optional[int]
    email: str
    password: str
    role: UserRole
    createdAt: datetime
    updatedAt: datetime
    totalTasksSolved: int
    lastActivityDate: Optional[datetime] 