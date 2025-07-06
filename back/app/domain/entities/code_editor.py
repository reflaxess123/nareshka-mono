from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from .enums import CodeLanguage, ExecutionStatus


@dataclass
class SupportedLanguage:
    id: str
    name: str
    language: CodeLanguage
    version: str
    dockerImage: str
    fileExtension: str
    runCommand: str
    timeoutSeconds: int
    memoryLimitMB: int
    isEnabled: bool
    createdAt: datetime
    updatedAt: datetime
    
    compileCommand: Optional[str] = None


@dataclass
class CodeExecution:
    id: str
    languageId: str
    sourceCode: str
    status: ExecutionStatus
    createdAt: datetime
    
    userId: Optional[int] = None
    blockId: Optional[str] = None
    stdin: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    exitCode: Optional[int] = None
    executionTimeMs: Optional[int] = None
    memoryUsedMB: Optional[float] = None
    containerLogs: Optional[str] = None
    errorMessage: Optional[str] = None
    completedAt: Optional[datetime] = None


@dataclass
class UserCodeSolution:
    id: str
    userId: int
    blockId: str
    languageId: str
    sourceCode: str
    isCompleted: bool
    executionCount: int
    successfulExecutions: int
    createdAt: datetime
    updatedAt: datetime
    
    lastExecutionId: Optional[str] = None


@dataclass
class TestCaseExecution:
    """Результат выполнения одного тест-кейса"""
    testCaseId: str
    testName: str
    input: str
    expectedOutput: str
    actualOutput: str
    passed: bool
    executionTimeMs: Optional[int] = None
    errorMessage: Optional[str] = None


@dataclass
class ValidationResult:
    """Результат валидации решения против всех тест-кейсов"""
    blockId: str
    sourceCode: str
    language: str
    allTestsPassed: bool
    totalTests: int
    passedTests: int
    score: float
    validatedAt: datetime
    testResults: List[TestCaseExecution]


@dataclass
class ExecutionStats:
    """Статистика выполнения кода пользователя"""
    totalExecutions: int
    successfulExecutions: int
    averageExecutionTime: float
    languageStats: List[dict] 