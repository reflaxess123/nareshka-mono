"""Progress types для внутреннего использования в services и repositories."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.shared.entities.enums import CodeLanguage


class TaskAttempt(BaseModel):
    """Попытка решения задачи пользователем"""

    id: str
    user_id: int
    block_id: str
    attempt_number: int
    source_code: str
    language: CodeLanguage
    is_successful: bool = False
    execution_time_ms: Optional[int] = None
    test_results: Dict[str, Any] = {}
    created_at: datetime


class TaskSolution(BaseModel):
    """Финальное решение задачи пользователем"""

    id: str
    user_id: int
    block_id: str
    source_code: str
    language: CodeLanguage
    is_successful: bool = False
    execution_time_ms: Optional[int] = None
    test_passed: int = 0
    test_total: int = 0
    created_at: datetime
    updated_at: datetime


class UserCategoryProgress(BaseModel):
    """Прогресс пользователя по категории"""

    id: str
    user_id: int
    main_category: str
    sub_category: Optional[str] = None
    total_blocks: int
    completed_blocks: int
    progress_percentage: float
    last_accessed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class LearningPath(BaseModel):
    """Путь обучения"""

    id: str
    name: str
    description: Optional[str] = None
    sequence: List[str]  # Block IDs in order
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class UserPathProgress(BaseModel):
    """Прогресс пользователя по пути обучения"""

    id: str
    user_id: int
    path_id: str
    current_position: int = 0
    completed_blocks: List[str] = []
    started_at: datetime
    last_accessed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class TestCase(BaseModel):
    """Тест-кейс для проверки кода"""

    id: str
    block_id: str
    test_name: str
    input_data: str
    expected_output: str
    is_public: bool = True
    execution_count: int = 0
    pass_rate: float = 0.0
    created_at: datetime
    updated_at: datetime


class TestValidationResult(BaseModel):
    """Результат выполнения тест-кейса"""

    id: str
    attempt_id: str
    test_case_id: str
    actual_output: str
    is_passed: bool
    execution_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
