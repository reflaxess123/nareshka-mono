"""API endpoints для работы с заданиями"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from app.application.dto.task_dto import (
    TaskCategoriesResponse,
    TaskCompaniesResponse,
    TasksListResponse,
)
from app.application.services.task_service import TaskService
from app.shared.dependencies import get_current_user_optional, get_task_service

router = APIRouter(prefix="/tasks", tags=["Tasks v2"])


@router.get("/items", response_model=TasksListResponse)
async def get_task_items(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(
        10, ge=1, le=100, description="Количество элементов на странице"
    ),
    mainCategories: List[str] = Query(
        [], description="Фильтр по основным категориям (множественный)"
    ),
    subCategories: List[str] = Query([], description="Подкатегории (множественный)"),
    q: Optional[str] = Query(None, description="Полнотекстовый поиск"),
    sortBy: str = Query("orderInFile", description="Поле для сортировки"),
    sortOrder: str = Query("asc", description="Порядок сортировки"),
    itemType: Optional[str] = Query(
        None, description="Тип: content_block, theory_quiz или all"
    ),
    onlyUnsolved: Optional[bool] = Query(None, description="Только нерешенные"),
    companies: Optional[str] = Query(
        None, description="Фильтр по компаниям (через запятую, deprecated)"
    ),
    companiesList: List[str] = Query(
        [], description="Фильтр по компаниям (множественный)"
    ),
    current_user=Depends(get_current_user_optional),
    task_service: TaskService = Depends(get_task_service),
):
    """Получение объединенного списка задач (content blocks + quiz карточки)"""
    user_id = current_user.id if current_user else None

    # Объединяем companies и companiesList
    final_companies = list(companiesList) if companiesList else []
    if companies:
        company_list = [c.strip() for c in companies.split(",") if c.strip()]
        for company in company_list:
            if company not in final_companies:
                final_companies.append(company)

    return await task_service.get_tasks(
        page=page,
        limit=limit,
        main_categories=mainCategories if mainCategories else None,
        sub_categories=subCategories if subCategories else None,
        search_query=q,
        sort_by=sortBy,
        sort_order=sortOrder,
        item_type=itemType,
        only_unsolved=onlyUnsolved,
        companies=final_companies if final_companies else None,
        user_id=user_id,
    )


@router.get("/categories", response_model=TaskCategoriesResponse)
async def get_task_categories(task_service: TaskService = Depends(get_task_service)):
    """Получение списка категорий заданий с подкатегориями и статистикой"""
    return await task_service.get_task_categories()


@router.get("/companies", response_model=TaskCompaniesResponse)
async def get_companies(
    mainCategories: List[str] = Query([], description="Фильтр по основным категориям"),
    subCategories: List[str] = Query([], description="Фильтр по подкатегориям"),
    task_service: TaskService = Depends(get_task_service),
):
    """Получение списка компаний из заданий с количеством"""
    return await task_service.get_task_companies(
        main_categories=mainCategories if mainCategories else None,
        sub_categories=subCategories if subCategories else None,
    )
