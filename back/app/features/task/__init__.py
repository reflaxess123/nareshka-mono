"""Task Feature"""

# Models
# DTOs
from app.features.task.dto.requests import (
    TaskAttemptCreateRequest,
    TaskSolutionCreateRequest,
)
from app.features.task.dto.responses import (
    TaskAttemptResponse,
    TaskCategoriesResponse,
    TaskCategoryResponse,
    TaskCompaniesResponse,
    TaskCompanyResponse,
    TaskResponse,
    TasksListResponse,
    TaskSolutionResponse,
)

# Exceptions
from app.features.task.exceptions.task_exceptions import (
    TaskAttemptError,
    TaskError,
    TaskNotFoundError,
    TaskSolutionError,
    TaskValidationError,
)

# Repository
from app.features.task.repositories.task_repository import TaskRepository

# Services
from app.features.task.services.task_service import TaskService
from app.shared.models.task_models import TaskAttempt, TaskSolution

# Router импортируется напрямую в main.py для избежания циклических импортов

__all__ = [
    # Models
    "TaskAttempt",
    "TaskSolution",
    # DTOs Requests
    "TaskAttemptCreateRequest",
    "TaskSolutionCreateRequest",
    # DTOs Responses
    "TaskResponse",
    "TasksListResponse",
    "TaskCategoryResponse",
    "TaskCategoriesResponse",
    "TaskCompanyResponse",
    "TaskCompaniesResponse",
    "TaskAttemptResponse",
    "TaskSolutionResponse",
    # Services
    "TaskService",
    # Repository
    "TaskRepository",
    # Exceptions
    "TaskError",
    "TaskNotFoundError",
    "TaskValidationError",
    "TaskAttemptError",
    "TaskSolutionError",
]
