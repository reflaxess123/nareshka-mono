"""Интерфейс репозитория пользователей"""

from abc import abstractmethod
from typing import Optional

from .base_repository import BaseRepository
from ...infrastructure.models.user_models import User


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