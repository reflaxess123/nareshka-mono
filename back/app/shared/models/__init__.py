# Infrastructure models - SQLAlchemy модели
from app.shared.database.connection import Base
from app.shared.entities.content import ContentBlock, ContentFile

from .code_execution_models import CodeExecution, SupportedLanguage, UserCodeSolution
from .enums import CardState, CodeLanguage, ExecutionStatus, ProgressStatus, UserRole
from .learning_path_models import LearningPath, UserPathProgress
from .progress_models import UserCategoryProgress
from .task_models import TaskAttempt, TaskSolution
from .test_case_models import TestCase, TestValidationResult
from .theory_models import TheoryCard, UserTheoryProgress
from .user_models import User

__all__ = [
    "Base",
    "User",
    "ContentFile",
    "ContentBlock",
    "UserContentProgress",
    "TheoryCard",
    "UserTheoryProgress",
    "SupportedLanguage",
    "CodeExecution",
    "UserCodeSolution",
    "UserCategoryProgress",
    "TaskAttempt",
    "TaskSolution",
    "LearningPath",
    "UserPathProgress",
    "TestCase",
    "TestValidationResult",
    "UserRole",
    "CardState",
    "ProgressStatus",
    "CodeLanguage",
    "ExecutionStatus",
]
