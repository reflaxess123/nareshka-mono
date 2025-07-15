"""
Progress Exceptions
"""

from .progress_exceptions import (
    # Progress Data
    ProgressNotFoundError,
    AttemptNotFoundError,
    SolutionNotFoundError,
    
    # Validation
    InvalidProgressDataError,
    InvalidAttemptDataError,
    InvalidSolutionDataError,
    InvalidTaskIdError,
    InvalidCategoryError,
    
    # Business Logic
    ProgressUpdateError,
    AttemptCreationError,
    SolutionCreationError,
    CategoryProgressError,
    ContentProgressError,
    
    # Constraints
    DuplicateAttemptError,
    DuplicateSolutionError,
    ProgressConflictError,
    
    # Analytics
    AnalyticsError,
    StatisticsError,
    ReportGenerationError
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
    "ReportGenerationError"
] 



