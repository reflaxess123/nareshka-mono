"""
Progress DTOs
"""

from .requests import (
    TaskAttemptCreateRequest,
    TaskSolutionCreateRequest,
    ContentProgressUpdateRequest,
    CategoryProgressUpdateRequest,
    ProgressAnalyticsRequest,
    UserStatsUpdateRequest
)

from .responses import (
    TaskAttemptResponse,
    TaskSolutionResponse,
    CategoryProgressResponse,
    ContentProgressResponse,
    UserProgressSummaryResponse,
    CategoryProgressSummaryResponse,
    GroupedCategoryProgressResponse,
    ProgressAnalyticsResponse,
    RecentActivityResponse,
    UserDetailedProgressResponse,
    ProgressStatsResponse,
    TaskProgressListResponse,
    AttemptHistoryResponse
)

__all__ = [
    # Requests
    "TaskAttemptCreateRequest",
    "TaskSolutionCreateRequest",
    "ContentProgressUpdateRequest",
    "CategoryProgressUpdateRequest",
    "ProgressAnalyticsRequest",
    "UserStatsUpdateRequest",
    
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
    "AttemptHistoryResponse"
] 



