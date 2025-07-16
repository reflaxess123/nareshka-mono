"""API роутер для работы с заданиями"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session

from app.features.task.services.task_service import TaskService
from app.shared.database import get_session
from app.features.task.dto.requests import TaskAttemptCreateRequest, TaskSolutionCreateRequest
from app.features.task.dto.responses import (
    TasksListResponse,
    TaskCategoriesResponse,
    TaskCompaniesResponse,
    TaskAttemptResponse,
    TaskSolutionResponse,
)
from app.shared.dependencies import (
    get_current_user_optional,
    get_current_user_required,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def get_task_service(db: Session = Depends(get_session)) -> TaskService:
    """Зависимость для получения сервиса task"""
    from app.features.task.repositories.task_repository import TaskRepository
    task_repository = TaskRepository(db)
    return TaskService(task_repository)


@router.get("/items", response_model=TasksListResponse)
async def get_task_items(
    request: Request,  # Добавляем request для отладки
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
    
    # 🔍 ENHANCED DEBUG LOGGING
    session_id = request.cookies.get("session_id")
    logger.info(f"🔍 DEBUG: get_task_items called", extra={
        "current_user": current_user is not None,
        "user_id": user_id,
        "user_email": current_user.email if current_user else None,
        "session_id": session_id[:10] + "..." if session_id else None,
        "cookies": dict(request.cookies),
        "page": page,
        "limit": limit
    })

    # Объединяем companies и companiesList
    final_companies = list(companiesList) if companiesList else []
    if companies:
        company_list = [c.strip() for c in companies.split(",") if c.strip()]
        for company in company_list:
            if company not in final_companies:
                final_companies.append(company)

    result = await task_service.get_tasks(
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
    
    # 🔍 DEBUG: Log result details
    if result.data:
        sample_tasks = result.data[:3]  # First 3 tasks
        logger.info(f"🔍 DEBUG: Returning {len(result.data)} tasks", extra={
            "user_id": user_id,
            "sample_progress": [
                {
                    "task_id": task.id[:10] + "...",
                    "title": task.title[:20] + "...",
                    "currentUserSolvedCount": task.currentUserSolvedCount
                }
                for task in sample_tasks
            ]
        })
    
    return result


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


# Дополнительные endpoints для работы с попытками и решениями

@router.post("/attempts", response_model=TaskAttemptResponse)
async def create_task_attempt(
    request: TaskAttemptCreateRequest,
    current_user=Depends(get_current_user_required),
    task_service: TaskService = Depends(get_task_service),
):
    """Создание попытки решения задачи"""
    try:
        return await task_service.create_task_attempt(current_user.id, request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка создания попытки: {str(e)}",
        )


@router.post("/solutions", response_model=TaskSolutionResponse)
async def create_task_solution(
    request: TaskSolutionCreateRequest,
    current_user=Depends(get_current_user_required),
    task_service: TaskService = Depends(get_task_service),
):
    """Создание решения задачи"""
    try:
        return await task_service.create_task_solution(current_user.id, request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка создания решения: {str(e)}",
        )


@router.get("/attempts", response_model=List[TaskAttemptResponse])
async def get_user_task_attempts(
    blockId: Optional[str] = Query(None, description="Фильтр по ID блока"),
    current_user=Depends(get_current_user_required),
    task_service: TaskService = Depends(get_task_service),
):
    """Получение попыток решения пользователя"""
    return await task_service.get_user_task_attempts(current_user.id, blockId)


@router.get("/solutions", response_model=List[TaskSolutionResponse])
async def get_user_task_solutions(
    blockId: Optional[str] = Query(None, description="Фильтр по ID блока"),
    current_user=Depends(get_current_user_required),
    task_service: TaskService = Depends(get_task_service),
):
    """Получение решений пользователя"""
    return await task_service.get_user_task_solutions(current_user.id, blockId) 


