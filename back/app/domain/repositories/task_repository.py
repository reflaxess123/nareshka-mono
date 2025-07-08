"""Интерфейс репозитория для работы с заданиями"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict, Any
from ..entities.task_types import Task, TaskCategory, TaskCompany


class TaskRepository(ABC):
    """Абстрактный репозиторий для работы с заданиями"""
    
    @abstractmethod
    async def get_tasks(
        self,
        page: int = 1,
        limit: int = 10,
        main_categories: Optional[List[str]] = None,
        sub_categories: Optional[List[str]] = None,
        search_query: Optional[str] = None,
        sort_by: str = "orderInFile",
        sort_order: str = "asc",
        item_type: Optional[str] = None,
        only_unsolved: Optional[bool] = None,
        companies: Optional[List[str]] = None,
        user_id: Optional[int] = None
    ) -> Tuple[List[Task], int]:
        """Получение объединенного списка заданий с пагинацией и фильтрацией"""
        pass
    
    @abstractmethod
    async def get_task_categories(self) -> List[TaskCategory]:
        """Получение списка категорий заданий с подкатегориями и статистикой"""
        pass
    
    @abstractmethod
    async def get_task_companies(
        self,
        main_categories: Optional[List[str]] = None,
        sub_categories: Optional[List[str]] = None
    ) -> List[TaskCompany]:
        """Получение списка компаний из заданий с количеством"""
        pass
    
    @abstractmethod
    async def get_content_blocks(
        self,
        main_categories: Optional[List[str]] = None,
        sub_categories: Optional[List[str]] = None,
        search_query: Optional[str] = None,
        only_unsolved: Optional[bool] = None,
        companies: Optional[List[str]] = None,
        user_id: Optional[int] = None
    ) -> List[Task]:
        """Получение заданий типа content_block"""
        pass
    
    @abstractmethod
    async def get_theory_quizzes(
        self,
        main_categories: Optional[List[str]] = None,
        sub_categories: Optional[List[str]] = None,
        search_query: Optional[str] = None,
        only_unsolved: Optional[bool] = None,
        user_id: Optional[int] = None
    ) -> List[Task]:
        """Получение заданий типа theory_quiz"""
        pass 