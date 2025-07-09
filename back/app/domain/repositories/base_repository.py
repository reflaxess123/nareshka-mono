"""Базовые интерфейсы репозиториев"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """Базовый интерфейс репозитория"""
    
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[T]:
        """Получить сущность по ID"""
        pass
    
    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """Получить все сущности с пагинацией"""
        pass
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Создать сущность"""
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """Обновить сущность"""
        pass
    
    @abstractmethod
    async def delete(self, id: int) -> bool:
        """Удалить сущность"""
        pass
    
    @abstractmethod
    async def exists(self, id: int) -> bool:
        """Проверить существование сущности"""
        pass 