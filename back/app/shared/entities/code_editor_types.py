"""Code editor types для внутреннего использования в services и repositories."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.shared.entities.enums import CodeLanguage, ExecutionStatus


class SupportedLanguage(BaseModel):
    """Поддерживаемый язык программирования"""

    id: str
    name: str
    language: CodeLanguage
    version: str
    file_extension: str
    docker_image: str
    compile_command: Optional[str] = None
    run_command: str
    timeout_seconds: int = 30
    memory_limit_mb: int = 128
    is_enabled: bool = True
    created_at: datetime
    updated_at: datetime


class CodeExecution(BaseModel):
    """Выполнение кода"""

    id: str
    user_id: Optional[int] = None
    block_id: Optional[str] = None
    source_code: str
    language: CodeLanguage
    status: ExecutionStatus
    execution_time_ms: Optional[int] = None
    memory_used_mb: Optional[float] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    exit_code: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class UserCodeSolution(BaseModel):
    """Пользовательское решение задачи"""

    id: str
    user_id: int
    block_id: str
    language_id: str
    source_code: str
    is_successful: bool = False
    execution_time_ms: Optional[int] = None
    memory_used_mb: Optional[float] = None
    test_results: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime


class TestCaseExecution(BaseModel):
    """Результат выполнения тест-кейса"""

    test_name: str
    input_data: str
    expected_output: str
    actual_output: str
    is_passed: bool
    execution_time_ms: Optional[int] = None
    memory_used_mb: Optional[float] = None
    error_message: Optional[str] = None


class ValidationResult(BaseModel):
    """Результат валидации кода"""

    is_valid: bool
    issues: List[str] = []
    warnings: List[str] = []
    execution_time_ms: Optional[int] = None


class ExecutionStats(BaseModel):
    """Статистика выполнения кода пользователем"""

    total_executions: int
    successful_executions: int
    average_execution_time_ms: float
    languages_used: List[str]
    success_rate: float
