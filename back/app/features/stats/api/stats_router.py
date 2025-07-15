"""API роутер для работы со статистикой"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.features.stats.services.stats_service import StatsService
from app.shared.database import get_session
from app.features.stats.dto.responses import (
    UserStatsOverviewResponse,
    ContentStatsResponse,
    TheoryStatsResponse,
    RoadmapStatsResponse,
    StatsHealthResponse,
)
from app.shared.dependencies import get_current_user_required
from app.features.stats.exceptions.stats_exceptions import (
    StatsDataNotFoundError,
    StatsCalculationError,
)

router = APIRouter(prefix="/stats", tags=["Stats"])


def get_stats_service(db: Session = Depends(get_session)) -> StatsService:
    """Зависимость для получения сервиса stats"""
    from app.features.stats.repositories.stats_repository import StatsRepository
    stats_repository = StatsRepository(db)
    return StatsService(stats_repository)


@router.get("/overview", response_model=UserStatsOverviewResponse)
async def get_user_stats_overview(
    current_user=Depends(get_current_user_required),
    stats_service: StatsService = Depends(get_stats_service),
):
    """Получение общей статистики пользователя"""
    try:
        stats = await stats_service.get_user_stats_overview(current_user.id)
        return stats
    except StatsDataNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except StatsCalculationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user stats overview: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user stats overview: {str(e)}",
        )


@router.get("/content", response_model=ContentStatsResponse)
async def get_content_stats(
    current_user=Depends(get_current_user_required),
    stats_service: StatsService = Depends(get_stats_service),
):
    """Получение детальной статистики по контенту"""
    try:
        stats = await stats_service.get_content_stats(current_user.id)
        return stats
    except StatsDataNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except StatsCalculationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content stats: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content stats: {str(e)}",
        )


@router.get("/theory", response_model=TheoryStatsResponse)
async def get_theory_stats(
    current_user=Depends(get_current_user_required),
    stats_service: StatsService = Depends(get_stats_service),
):
    """Получение детальной статистики по теории"""
    try:
        stats = await stats_service.get_theory_stats(current_user.id)
        return stats
    except StatsDataNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except StatsCalculationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get theory stats: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get theory stats: {str(e)}",
        )


@router.get("/roadmap", response_model=RoadmapStatsResponse)
async def get_roadmap_stats(
    current_user=Depends(get_current_user_required),
    stats_service: StatsService = Depends(get_stats_service),
):
    """Получение roadmap статистики по категориям"""
    try:
        stats = await stats_service.get_roadmap_stats(current_user.id)
        return stats
    except StatsDataNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except StatsCalculationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get roadmap stats: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get roadmap stats: {str(e)}",
        )


@router.get("/health", response_model=StatsHealthResponse)
async def health_check(
    stats_service: StatsService = Depends(get_stats_service),
):
    """Проверка работоспособности Stats API"""
    return await stats_service.get_stats_health()


# Дополнительные endpoints для расширенной аналитики

@router.get("/summary")
async def get_user_progress_summary(
    current_user=Depends(get_current_user_required),
    stats_service: StatsService = Depends(get_stats_service),
):
    """Получение краткого резюме прогресса пользователя"""
    try:
        summary = await stats_service.get_user_progress_summary(current_user.id)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get progress summary: {str(e)}",
        )


@router.get("/categories/comparison")
async def get_category_comparison(
    current_user=Depends(get_current_user_required),
    stats_service: StatsService = Depends(get_stats_service),
):
    """Получение сравнения прогресса по категориям"""
    try:
        comparison = await stats_service.get_category_comparison(current_user.id)
        return comparison
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get category comparison: {str(e)}",
        ) 


