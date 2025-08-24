"""Репозитории task feature"""

from .content_block_repository import ContentBlockRepository
from .task_attempt_repository import TaskAttemptRepository
from .task_repository import TaskRepository
from .theory_quiz_repository import TheoryQuizRepository

__all__ = [
    "TaskRepository",  # DEPRECATED - используйте специализированные репозитории
    "ContentBlockRepository",
    "TheoryQuizRepository",
    "TaskAttemptRepository",
]
