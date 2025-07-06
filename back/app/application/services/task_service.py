"""Сервис для работы с заданиями"""

from typing import List, Optional, Tuple
from ...domain.entities.task import Task, TaskCategory, TaskCompany
from ...domain.repositories.task_repository import TaskRepository
from ..dto.task_dto import (
    TasksListResponse,
    TaskResponse,
    TaskCategoriesResponse,
    TaskCompaniesResponse
)


class TaskService:
    """Сервис для работы с заданиями"""
    
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository
    
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
    ) -> TasksListResponse:
        """Получение объединенного списка заданий с пагинацией и фильтрацией"""
        # Преобразуем старый параметр companies в список
        if companies and isinstance(companies, str):
            companies = [c.strip() for c in companies.split(',') if c.strip()]
        
        tasks, total = await self.task_repository.get_tasks(
            page=page,
            limit=limit,
            main_categories=main_categories,
            sub_categories=sub_categories,
            search_query=search_query,
            sort_by=sort_by,
            sort_order=sort_order,
            item_type=item_type,
            only_unsolved=only_unsolved,
            companies=companies,
            user_id=user_id
        )
        
        task_responses = [TaskResponse.from_domain(task) for task in tasks]
        
        return TasksListResponse.create(task_responses, total, page, limit)
    
    async def get_task_categories(self) -> TaskCategoriesResponse:
        """Получение списка категорий заданий"""
        categories = await self.task_repository.get_task_categories()
        return TaskCategoriesResponse(categories=categories)
    
    async def get_task_companies(
        self,
        main_categories: Optional[List[str]] = None,
        sub_categories: Optional[List[str]] = None
    ) -> TaskCompaniesResponse:
        """Получение списка компаний из заданий"""
        companies = await self.task_repository.get_task_companies(
            main_categories=main_categories,
            sub_categories=sub_categories
        )
        return TaskCompaniesResponse(companies=companies) 