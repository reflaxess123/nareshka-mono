"""Интерфейс репозитория пользователей"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.shared.models.user_models import User


class BaseRepository(ABC):
    """Базовый интерфейс репозитория"""

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[User]:
        """Получить по ID"""
        pass

    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Получить все с пагинацией"""
        pass

    @abstractmethod
    async def create(self, entity: User) -> User:
        """Создать"""
        pass

    @abstractmethod
    async def update(self, entity: User) -> User:
        """Обновить"""
        pass

    @abstractmethod
    async def delete(self, id: int) -> bool:
        """Удалить"""
        pass

    @abstractmethod
    async def exists(self, id: int) -> bool:
        """Проверить существование"""
        pass


class UserRepository(BaseRepository):
    """Интерфейс репозитория пользователей"""

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        pass

    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        """Проверить существование email"""
        pass
