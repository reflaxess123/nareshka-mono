"""DTO task feature"""

from .requests import (
    TaskAttemptCreateRequest,
    TaskSolutionCreateRequest,
    TaskFilterRequest,
)
from .responses import (
    TaskResponse,
    TasksListResponse,
    TaskCategoryResponse,
    TaskCategoriesResponse,
    TaskCompanyResponse,
    TaskCompaniesResponse,
    TaskAttemptResponse,
    TaskSolutionResponse,
    FileResponse,
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



