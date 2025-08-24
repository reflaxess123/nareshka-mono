"""DTO task feature"""

from .requests import (
    TaskAttemptCreateRequest,
    TaskFilterRequest,
    TaskSolutionCreateRequest,
)
from .responses import (
    FileResponse,
    TaskAttemptResponse,
    TaskCategoriesResponse,
    TaskCategoryResponse,
    TaskCompaniesResponse,
    TaskCompanyResponse,
    TaskResponse,
    TasksListResponse,
    TaskSolutionResponse,
)

__all__ = [
    # Requests
    "TaskAttemptCreateRequest",
    "TaskSolutionCreateRequest",
    "TaskFilterRequest",
    # Responses
    "TaskResponse",
    "TasksListResponse",
    "TaskCategoryResponse",
    "TaskCategoriesResponse",
    "TaskCompanyResponse",
    "TaskCompaniesResponse",
    "TaskAttemptResponse",
    "TaskSolutionResponse",
    "FileResponse",
]
