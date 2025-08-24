"""
Progress Exceptions
"""

from .progress_exceptions import (
    # Analytics
    AnalyticsError,
    AttemptCreationError,
    AttemptNotFoundError,
    CategoryProgressError,
    ContentProgressError,
    # Constraints
    DuplicateAttemptError,
    DuplicateSolutionError,
    InvalidAttemptDataError,
    InvalidCategoryError,
    # Validation
    InvalidProgressDataError,
    InvalidSolutionDataError,
    InvalidTaskIdError,
    ProgressConflictError,
    # Progress Data
    ProgressNotFoundError,
    # Business Logic
    ProgressUpdateError,
    ReportGenerationError,
    SolutionCreationError,
    SolutionNotFoundError,
    StatisticsError,
)

__all__ = [
    # Progress Data
    "ProgressNotFoundError",
    "AttemptNotFoundError",
    "SolutionNotFoundError",
    # Validation
    "InvalidProgressDataError",
    "InvalidAttemptDataError",
    "InvalidSolutionDataError",
    "InvalidTaskIdError",
    "InvalidCategoryError",
    # Business Logic
    "ProgressUpdateError",
    "AttemptCreationError",
    "SolutionCreationError",
    "CategoryProgressError",
    "ContentProgressError",
    # Constraints
    "DuplicateAttemptError",
    "DuplicateSolutionError",
    "ProgressConflictError",
    # Analytics
    "AnalyticsError",
    "StatisticsError",
    "ReportGenerationError",
]
