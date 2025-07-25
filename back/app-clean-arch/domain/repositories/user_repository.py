"""Интерфейс репозитория пользователей"""

from abc import abstractmethod
from typing import Optional

from app.infrastructure.models.user_models import User

from .base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Интерфейс репозитория пользователей"""

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        pass

    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        """Проверить существование email"""
        pass
