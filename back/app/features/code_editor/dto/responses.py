"""Response DTOs для code_editor feature"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.shared.models.enums import CodeLanguage, ExecutionStatus


class SupportedLanguageResponse(BaseModel):
    """Поддерживаемый язык программирования"""

    id: str
    name: str
    language: CodeLanguage
    version: str
    fileExtension: str
    timeoutSeconds: int
    memoryLimitMB: int
    isEnabled: bool


class CodeExecutionResponse(BaseModel):
    """Результат выполнения кода"""

    id: str
    userId: Optional[int] = None
    blockId: Optional[str] = None
    languageId: str
    sourceCode: str
    stdin: Optional[str] = None
    status: ExecutionStatus
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    exitCode: Optional[int] = None
    executionTimeMs: Optional[int] = None
    memoryUsedMB: Optional[float] = None
    containerLogs: Optional[str] = None
    errorMessage: Optional[str] = None
    createdAt: datetime
    completedAt: Optional[datetime] = None


class UserCodeSolutionResponse(BaseModel):
    """Решение пользователя"""

    id: str
    userId: int
    blockId: str
    languageId: str
    sourceCode: str
    isCompleted: bool
    executionCount: int
    successfulExecutions: int
    lastExecutionId: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime


class LanguageStatResponse(BaseModel):
    """Статистика по языку"""

    language: CodeLanguage
    name: str
    executions: int


class ExecutionStatsResponse(BaseModel):
    """Статистика выполнений"""

    totalExecutions: int
    successfulExecutions: int
    averageExecutionTime: float
    languageStats: List[Dict[str, Any]]


class TestCaseResponse(BaseModel):
    """Тест-кейс"""

    id: str
    blockId: str
    name: str
    description: Optional[str] = None
    input: str = ""
    expectedOutput: str
    isPublic: bool = True
    difficulty: str = "BASIC"
    weight: float = 1.0
    timeoutSeconds: int = 5
    isActive: bool = True
    orderIndex: int = 0
    isAIGenerated: bool = False
    generationPrompt: Optional[str] = None
    generatedAt: Optional[datetime] = None
    generationModel: Optional[str] = None
    executionCount: int = 0
    passRate: float = 0.0
    createdAt: datetime
    updatedAt: datetime


class TestCasesResponse(BaseModel):
    """Список тест-кейсов для блока"""

    blockId: str
    testCases: List[TestCaseResponse]
    totalTests: int
    publicTests: int
    hiddenTests: int
    lastGenerated: Optional[datetime] = None


class TestCaseExecutionResponse(BaseModel):
    """Результат выполнения тест-кейса"""

    testCaseId: str
    testName: str
    input: str
    expectedOutput: str
    actualOutput: str
    passed: bool
    executionTimeMs: Optional[int] = None
    errorMessage: Optional[str] = None


class ValidationResultResponse(BaseModel):
    """Результат валидации решения"""

    blockId: str
    sourceCode: str
    language: str
    allTestsPassed: bool
    totalTests: int
    passedTests: int
    score: float
    validatedAt: datetime
    testResults: List[TestCaseExecutionResponse]


class HealthResponse(BaseModel):
    """Ответ health check"""

    status: str
    module: str
    supportedLanguages: int
    totalExecutions: int
