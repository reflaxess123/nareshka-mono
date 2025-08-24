"""Интерфейс репозитория пользователей"""

from abc import ABC, abstractmethod
from typing import Optional

from app.shared.models.user_models import User


class UserRepository(ABC):
    """Минималистичный интерфейс репозитория пользователей"""

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        pass

    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        """Проверить существование email"""
        pass

    @abstractmethod
    async def create(self, entity: User) -> User:
        """Создать пользователя"""
        pass
