"""
Progress DTOs
"""

from .requests import (
    CategoryProgressUpdateRequest,
    ContentProgressUpdateRequest,
    ProgressAnalyticsRequest,
    TaskAttemptCreateRequest,
    TaskSolutionCreateRequest,
)
from .responses import (
    AttemptHistoryResponse,
    CategoryProgressResponse,
    CategoryProgressSummaryResponse,
    ContentProgressResponse,
    GroupedCategoryProgressResponse,
    ProgressAnalyticsResponse,
    ProgressStatsResponse,
    RecentActivityResponse,
    TaskAttemptResponse,
    TaskProgressListResponse,
    TaskSolutionResponse,
    UserDetailedProgressResponse,
    UserProgressSummaryResponse,
)

__all__ = [
    # Requests
    "TaskAttemptCreateRequest",
    "TaskSolutionCreateRequest",
    "ContentProgressUpdateRequest",
    "CategoryProgressUpdateRequest",
    "ProgressAnalyticsRequest",
    # Responses
    "TaskAttemptResponse",
    "TaskSolutionResponse",
    "CategoryProgressResponse",
    "ContentProgressResponse",
    "UserProgressSummaryResponse",
    "CategoryProgressSummaryResponse",
    "GroupedCategoryProgressResponse",
    "ProgressAnalyticsResponse",
    "RecentActivityResponse",
    "UserDetailedProgressResponse",
    "ProgressStatsResponse",
    "TaskProgressListResponse",
    "AttemptHistoryResponse",
]
