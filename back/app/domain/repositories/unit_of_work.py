"""Unit of Work интерфейс"""

from abc import ABC, abstractmethod
from typing import Protocol
from .user_repository import UserRepository
from .content_repository import ContentRepository
from .theory_repository import TheoryRepository
from .task_repository import TaskRepository


class UnitOfWork(ABC):
    """Интерфейс Unit of Work для управления транзакциями"""
    
    users: UserRepository
    content: ContentRepository
    theory: TheoryRepository
    tasks: TaskRepository
    
    @abstractmethod
    async def __aenter__(self):
        """Начало транзакции"""
        pass
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Завершение транзакции с rollback при ошибке"""
        pass
    
    @abstractmethod
    async def commit(self):
        """Подтверждение транзакции"""
        pass
    
    @abstractmethod
    async def rollback(self):
        """Откат транзакции"""
        pass 