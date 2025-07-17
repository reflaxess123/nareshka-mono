"""Репозитории task feature"""

from .task_repository import TaskRepository
from .content_block_repository import ContentBlockRepository
from .theory_quiz_repository import TheoryQuizRepository
from .task_attempt_repository import TaskAttemptRepository

__all__ = [
    "TaskRepository",  # DEPRECATED - используйте специализированные репозитории
    "ContentBlockRepository",
    "TheoryQuizRepository", 
    "TaskAttemptRepository",
] 



