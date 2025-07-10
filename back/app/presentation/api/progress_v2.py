"""API для работы с прогрессом v2"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dto.progress_dto import (
    ProgressAnalyticsDTO,
    TaskAttemptCreateDTO,
    TaskAttemptResponseDTO,
    UserDetailedProgressResponseDTO,
)
from app.application.services.progress_service import ProgressService
from app.infrastructure.models.user_models import User
from app.shared.dependencies import get_current_user_optional, get_progress_service

router = APIRouter(prefix="/progress", tags=["progress"])


@router.post("/attempts", response_model=TaskAttemptResponseDTO)
async def create_task_attempt(
    attempt_data: TaskAttemptCreateDTO,
    current_user: Optional[User] = Depends(get_current_user_optional),
    progress_service: ProgressService = Depends(get_progress_service),
):
    """Создание попытки решения задачи"""

    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Устанавливаем userId из текущего пользователя
    attempt_data.userId = current_user.id

    try:
        result = await progress_service.create_task_attempt(attempt_data)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create task attempt: {str(e)}",
        )


@router.get("/user/my/detailed", response_model=UserDetailedProgressResponseDTO)
async def get_my_detailed_progress(
    current_user: Optional[User] = Depends(get_current_user_optional),
    progress_service: ProgressService = Depends(get_progress_service),
):
    """Получение детального прогресса текущего пользователя"""

    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        result = await progress_service.get_user_detailed_progress(current_user.id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user progress: {str(e)}",
        )


@router.get("/user/{user_id}/detailed", response_model=UserDetailedProgressResponseDTO)
async def get_user_detailed_progress(
    user_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    progress_service: ProgressService = Depends(get_progress_service),
):
    """Получение детального прогресса пользователя по ID (для админов)"""

    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Проверяем, что пользователь админ или запрашивает свой прогресс
    if current_user.role != "ADMIN" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    try:
        result = await progress_service.get_user_detailed_progress(user_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user progress: {str(e)}",
        )


@router.get("/analytics", response_model=ProgressAnalyticsDTO)
async def get_progress_analytics(
    current_user: Optional[User] = Depends(get_current_user_optional),
    progress_service: ProgressService = Depends(get_progress_service),
):
    """Получение аналитики прогресса (только для админов)"""

    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Проверяем, что пользователь админ
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required.",
        )

    try:
        result = await progress_service.get_progress_analytics()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get progress analytics: {str(e)}",
        )


@router.get("/health")
async def health_check():
    """Проверка работоспособности Progress API"""
    return {"status": "healthy", "module": "progress"}
