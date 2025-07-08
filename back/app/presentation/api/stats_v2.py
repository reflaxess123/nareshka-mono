"""API для работы со статистикой v2"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from ...application.dto.stats_dto import (
    UserStatsOverviewDTO,
    ContentStatsDTO,
    TheoryStatsDTO,
    RoadmapStatsDTO
)
from ...application.services.stats_service import StatsService
from ...infrastructure.models.user_models import User
from ...shared.dependencies import get_current_user_optional, get_stats_service

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview", response_model=UserStatsOverviewDTO)
async def get_user_stats_overview(
    current_user: Optional[User] = Depends(get_current_user_optional),
    stats_service: StatsService = Depends(get_stats_service)
):
    """Получение общей статистики пользователя"""
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        stats = await stats_service.get_user_stats_overview(current_user.id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user stats overview: {str(e)}"
        )


@router.get("/content", response_model=ContentStatsDTO)
async def get_content_stats(
    current_user: Optional[User] = Depends(get_current_user_optional),
    stats_service: StatsService = Depends(get_stats_service)
):
    """Получение детальной статистики по контенту"""
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        stats = await stats_service.get_content_stats(current_user.id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content stats: {str(e)}"
        )


@router.get("/theory", response_model=TheoryStatsDTO)
async def get_theory_stats(
    current_user: Optional[User] = Depends(get_current_user_optional),
    stats_service: StatsService = Depends(get_stats_service)
):
    """Получение детальной статистики по теории"""
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        stats = await stats_service.get_theory_stats(current_user.id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get theory stats: {str(e)}"
        )


@router.get("/roadmap", response_model=RoadmapStatsDTO)
async def get_roadmap_stats(
    current_user: Optional[User] = Depends(get_current_user_optional),
    stats_service: StatsService = Depends(get_stats_service)
):
    """Получение roadmap статистики по категориям"""
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        stats = await stats_service.get_roadmap_stats(current_user.id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get roadmap stats: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Проверка работоспособности Stats API"""
    return {"status": "healthy", "module": "stats"} 