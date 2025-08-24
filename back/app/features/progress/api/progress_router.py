"""
API роутер для progress feature
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.rate_limiter import limiter
from app.shared.database.base import DatabaseManager

# Импорты auth для проверки пользователей
from app.shared.dependencies import (
    get_current_admin_session,
    get_current_user_required,
    get_db_manager as get_database_manager,
)
from app.shared.models.user_models import User

from ..dto.requests import (
    CategoryProgressUpdateRequest,
    ContentProgressUpdateRequest,
    ProgressAnalyticsRequest,
    TaskAttemptCreateRequest,
    TaskSolutionCreateRequest,
)
from ..dto.responses import (
    AttemptHistoryResponse,
    CategoryProgressResponse,
    ContentProgressResponse,
    ProgressAnalyticsResponse,
    ProgressStatsResponse,
    RecentActivityResponse,
    TaskAttemptResponse,
    TaskSolutionResponse,
    UserDetailedProgressResponse,
    UserProgressSummaryResponse,
)
from ..exceptions.progress_exceptions import (
    InvalidProgressDataError,
)
from ..repositories.progress_repository import ProgressRepository
from ..services.progress_service import ProgressService

router = APIRouter(prefix="/progress", tags=["Progress"])

# === Dependencies ===


def get_progress_repository(
    db_manager: DatabaseManager = Depends(get_database_manager),
) -> ProgressRepository:
    """Получение репозитория прогресса"""
    return ProgressRepository()


def get_progress_service(
    progress_repository: ProgressRepository = Depends(get_progress_repository),
) -> ProgressService:
    """Получение сервиса прогресса"""
    return ProgressService(progress_repository)


# === Task Attempts ===


@router.post(
    "/attempts",
    response_model=TaskAttemptResponse,
    summary="Создание попытки решения",
    description="Создание новой попытки решения задачи",
)
@limiter.limit("100/minute")  # Лимит для попыток решения
async def create_task_attempt(
    request: TaskAttemptCreateRequest,
    current_user: User = Depends(get_current_user_required),
    progress_service: ProgressService = Depends(get_progress_service),
) -> TaskAttemptResponse:
    """Создание попытки решения задачи"""
    try:
        # Проверяем что пользователь создает попытку для себя
        if request.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Можно создавать попытки только для себя",
            )

        return await progress_service.create_task_attempt(request)

    except InvalidProgressDataError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании попытки решения",
        )


@router.get(
    "/attempts",
    response_model=List[TaskAttemptResponse],
    summary="Получение попыток пользователя",
    description="Получение списка попыток решения задач пользователя",
)
async def get_user_attempts(
    current_user: User = Depends(get_current_user_required),
    task_id: Optional[str] = Query(None, description="Фильтр по ID задачи"),
    limit: int = Query(50, description="Лимит результатов"),
    progress_service: ProgressService = Depends(get_progress_service),
) -> List[TaskAttemptResponse]:
    """Получение попыток пользователя"""
    return await progress_service.get_user_attempts(
        user_id=current_user.id, task_id=task_id, limit=limit
    )


@router.get(
    "/attempts/{task_id}/history",
    response_model=AttemptHistoryResponse,
    summary="История попыток по задаче",
    description="Получение полной истории попыток решения конкретной задачи",
)
async def get_attempt_history(
    task_id: str,
    current_user: User = Depends(get_current_user_required),
    progress_service: ProgressService = Depends(get_progress_service),
) -> AttemptHistoryResponse:
    """Получение истории попыток для задачи"""
    return await progress_service.get_attempt_history(current_user.id, task_id)


# === Task Solutions ===


@router.post(
    "/solutions",
    response_model=TaskSolutionResponse,
    summary="Создание решения задачи",
    description="Создание или обновление решения задачи",
)
async def create_task_solution(
    request: TaskSolutionCreateRequest,
    current_user: User = Depends(get_current_user_required),
    progress_service: ProgressService = Depends(get_progress_service),
) -> TaskSolutionResponse:
    """Создание решения задачи"""
    try:
        # Проверяем что пользователь создает решение для себя
        if request.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Можно создавать решения только для себя",
            )

        return await progress_service.create_task_solution(request)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании решения",
        )


@router.get(
    "/solutions",
    response_model=List[TaskSolutionResponse],
    summary="Получение решений пользователя",
    description="Получение списка решений задач пользователя",
)
async def get_user_solutions(
    current_user: User = Depends(get_current_user_required),
    limit: int = Query(50, description="Лимит результатов"),
    progress_service: ProgressService = Depends(get_progress_service),
) -> List[TaskSolutionResponse]:
    """Получение решений пользователя"""
    return await progress_service.get_user_solutions(
        user_id=current_user.id, limit=limit
    )


@router.get(
    "/solutions/{task_id}",
    response_model=TaskSolutionResponse,
    summary="Получение решения задачи",
    description="Получение конкретного решения задачи",
)
async def get_task_solution(
    task_id: str,
    current_user: User = Depends(get_current_user_required),
    progress_service: ProgressService = Depends(get_progress_service),
) -> TaskSolutionResponse:
    """Получение решения задачи"""
    solution = await progress_service.get_task_solution(current_user.id, task_id)

    if not solution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Решение не найдено"
        )

    return solution


# === Content Progress ===


@router.put(
    "/content",
    response_model=ContentProgressResponse,
    summary="Обновление прогресса по контенту",
    description="Обновление прогресса изучения контентного блока",
)
async def update_content_progress(
    request: ContentProgressUpdateRequest,
    current_user: User = Depends(get_current_user_required),
    progress_service: ProgressService = Depends(get_progress_service),
) -> ContentProgressResponse:
    """Обновление прогресса по контенту"""
    try:
        # Проверяем что пользователь обновляет свой прогресс
        if request.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Можно обновлять только свой прогресс",
            )

        return await progress_service.update_content_progress(request)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении прогресса по контенту",
        )


@router.get(
    "/content",
    response_model=List[ContentProgressResponse],
    summary="Получение прогресса по контенту",
    description="Получение прогресса изучения контентных блоков",
)
async def get_user_content_progress(
    current_user: User = Depends(get_current_user_required),
    block_id: Optional[str] = Query(None, description="Фильтр по ID блока"),
    progress_service: ProgressService = Depends(get_progress_service),
) -> List[ContentProgressResponse]:
    """Получение прогресса по контенту"""
    return await progress_service.get_user_content_progress(
        user_id=current_user.id, block_id=block_id
    )


# === Category Progress ===


@router.put(
    "/categories",
    response_model=CategoryProgressResponse,
    summary="Обновление прогресса по категории",
    description="Обновление прогресса изучения категории",
)
async def update_category_progress(
    request: CategoryProgressUpdateRequest,
    current_admin: User = Depends(
        get_current_admin_session
    ),  # Только админ может обновлять прогресс по категориям
    progress_service: ProgressService = Depends(get_progress_service),
) -> CategoryProgressResponse:
    """Обновление прогресса по категории"""
    try:
        return await progress_service.update_category_progress(request)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении прогресса по категории",
        )


@router.get(
    "/categories",
    response_model=List[CategoryProgressResponse],
    summary="Получение прогресса по категориям",
    description="Получение прогресса изучения категорий",
)
async def get_user_category_progress(
    current_user: User = Depends(get_current_user_required),
    main_category: Optional[str] = Query(
        None, description="Фильтр по основной категории"
    ),
    progress_service: ProgressService = Depends(get_progress_service),
) -> List[CategoryProgressResponse]:
    """Получение прогресса по категориям"""
    return await progress_service.get_category_progress(
        user_id=current_user.id, main_category=main_category
    )


# === User Progress ===


@router.get(
    "/summary",
    response_model=UserProgressSummaryResponse,
    summary="Сводка прогресса пользователя",
    description="Получение краткой сводки прогресса текущего пользователя",
)
async def get_user_progress_summary(
    current_user: User = Depends(get_current_user_required),
    progress_service: ProgressService = Depends(get_progress_service),
) -> UserProgressSummaryResponse:
    """Получение сводки прогресса пользователя"""
    return await progress_service.get_user_progress_summary(current_user.id)


@router.get(
    "/detailed",
    response_model=UserDetailedProgressResponse,
    summary="Детальный прогресс пользователя",
    description="Получение детального прогресса текущего пользователя",
)
async def get_user_detailed_progress(
    current_user: User = Depends(get_current_user_required),
    progress_service: ProgressService = Depends(get_progress_service),
) -> UserDetailedProgressResponse:
    """Получение детального прогресса пользователя"""
    return await progress_service.get_user_detailed_progress(current_user.id)


@router.get(
    "/user/my/detailed",
    response_model=UserDetailedProgressResponse,
    summary="Детальный прогресс пользователя (альтернативный путь)",
    description="Получение детального прогресса текущего пользователя",
)
async def get_my_detailed_progress(
    current_user: User = Depends(get_current_user_required),
    progress_service: ProgressService = Depends(get_progress_service),
) -> UserDetailedProgressResponse:
    """Получение детального прогресса пользователя (альтернативный путь)"""
    return await progress_service.get_user_detailed_progress(current_user.id)


@router.get(
    "/stats",
    response_model=ProgressStatsResponse,
    summary="Статистика прогресса",
    description="Получение статистики прогресса за определенный период",
)
async def get_progress_stats(
    current_user: User = Depends(get_current_user_required),
    period: str = Query("week", description="Период: day, week, month"),
    progress_service: ProgressService = Depends(get_progress_service),
) -> ProgressStatsResponse:
    """Получение статистики прогресса"""
    return await progress_service.get_progress_stats(
        user_id=current_user.id, period=period
    )


# === Analytics ===


@router.get(
    "/analytics",
    response_model=ProgressAnalyticsResponse,
    summary="Аналитика прогресса",
    description="Получение аналитики прогресса (для администраторов)",
)
async def get_progress_analytics(
    current_admin: User = Depends(get_current_admin_session),
    user_id: Optional[int] = Query(None, description="ID пользователя"),
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    limit: int = Query(20, description="Лимит результатов"),
    offset: int = Query(0, description="Смещение"),
    progress_service: ProgressService = Depends(get_progress_service),
) -> ProgressAnalyticsResponse:
    """Получение аналитики прогресса"""
    request = ProgressAnalyticsRequest(
        user_id=user_id, category=category, limit=limit, offset=offset
    )

    return await progress_service.get_progress_analytics(request)


@router.get(
    "/activity",
    response_model=List[RecentActivityResponse],
    summary="Недавняя активность",
    description="Получение недавней активности пользователей",
)
async def get_recent_activity(
    current_user: User = Depends(get_current_user_required),
    limit: int = Query(20, description="Лимит результатов"),
    progress_service: ProgressService = Depends(get_progress_service),
) -> List[RecentActivityResponse]:
    """Получение недавней активности"""
    return await progress_service.get_recent_activity(
        user_id=current_user.id, limit=limit
    )


# === Admin Endpoints ===


@router.get(
    "/admin/users/{user_id}/summary",
    response_model=UserProgressSummaryResponse,
    summary="Сводка прогресса пользователя (админ)",
    description="Получение сводки прогресса любого пользователя (только для админа)",
)
async def get_admin_user_progress_summary(
    user_id: int,
    current_admin: User = Depends(get_current_admin_session),
    progress_service: ProgressService = Depends(get_progress_service),
) -> UserProgressSummaryResponse:
    """Получение сводки прогресса пользователя (админ)"""
    return await progress_service.get_user_progress_summary(user_id)


@router.get(
    "/admin/users/{user_id}/detailed",
    response_model=UserDetailedProgressResponse,
    summary="Детальный прогресс пользователя (админ)",
    description="Получение детального прогресса любого пользователя (только для админа)",
)
async def get_admin_user_detailed_progress(
    user_id: int,
    current_admin: User = Depends(get_current_admin_session),
    progress_service: ProgressService = Depends(get_progress_service),
) -> UserDetailedProgressResponse:
    """Получение детального прогресса пользователя (админ)"""
    return await progress_service.get_user_detailed_progress(user_id)


@router.get(
    "/admin/activity/all",
    response_model=List[RecentActivityResponse],
    summary="Вся недавняя активность (админ)",
    description="Получение недавней активности всех пользователей (только для админа)",
)
async def get_all_recent_activity(
    current_admin: User = Depends(get_current_admin_session),
    limit: int = Query(50, description="Лимит результатов"),
    progress_service: ProgressService = Depends(get_progress_service),
) -> List[RecentActivityResponse]:
    """Получение недавней активности всех пользователей"""
    return await progress_service.get_recent_activity(
        user_id=None,  # Все пользователи
        limit=limit,
    )
