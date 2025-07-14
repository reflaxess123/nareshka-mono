"""
Progress Feature - Отслеживание прогресса обучения

Этот модуль реализует систему прогресса пользователей:
- Отслеживание выполненных задач
- Статистика обучения
- Прогресс по темам и курсам
- Achievement система
- Аналитика успеваемости
"""

from app.shared.models.enums import ProgressStatus
from app.shared.models.progress_models import UserCategoryProgress
from app.shared.models.content_models import UserContentProgress

from .repositories import ProgressRepository
from .services import ProgressService
# Router импортируется напрямую в main.py для избежания циклических импортов

from .dto.requests import (
    ContentProgressUpdateRequest,
    CategoryProgressUpdateRequest,
    ProgressAnalyticsRequest,
    UserStatsUpdateRequest
)

from .dto.responses import (
    CategoryProgressResponse,
    ContentProgressResponse,
    UserProgressSummaryResponse,
    ProgressAnalyticsResponse,
    RecentActivityResponse,
    UserDetailedProgressResponse,
    ProgressStatsResponse,
    AttemptHistoryResponse
)

__all__ = [
    # Models
    "ProgressStatus",
    "UserCategoryProgress",
    "UserContentProgress",
    
    # Repositories
    "ProgressRepository",
    
    # Services
    "ProgressService",
    

    
    # DTOs - Requests
    "ContentProgressUpdateRequest",
    "CategoryProgressUpdateRequest",
    "ProgressAnalyticsRequest",
    "UserStatsUpdateRequest",
    
    # DTOs - Responses
    "CategoryProgressResponse",
    "ContentProgressResponse",
    "UserProgressSummaryResponse",
    "ProgressAnalyticsResponse",
    "RecentActivityResponse",
    "UserDetailedProgressResponse",
    "ProgressStatsResponse",
    "AttemptHistoryResponse"
]

__version__ = "1.0.0" 



