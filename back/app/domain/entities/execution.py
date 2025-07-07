"""Сущности выполнения кода"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass

from .enums import CodeLanguage, ExecutionStatus


@dataclass
class SupportedLanguage:
    """Доменная сущность поддерживаемого языка"""
    id: str
    name: str
    language: CodeLanguage
    version: str
    dockerImage: str
    fileExtension: str
    compileCommand: Optional[str]
    runCommand: str
    timeoutSeconds: int
    memoryLimitMB: int
    isEnabled: bool
    createdAt: datetime
    updatedAt: datetime


@dataclass
class CodeExecution:
    """Доменная сущность выполнения кода"""
    id: str
    userId: Optional[int]
    blockId: Optional[str]
    languageId: str
    sourceCode: str
    stdin: Optional[str]
    status: ExecutionStatus
    stdout: Optional[str]
    stderr: Optional[str]
    exitCode: Optional[int]
    executionTimeMs: Optional[int]
    memoryUsedMB: Optional[int]
    containerLogs: Optional[str]
    errorMessage: Optional[str]
    createdAt: datetime
    completedAt: Optional[datetime]


@dataclass
class UserCodeSolution:
    """Доменная сущность решения пользователя"""
    id: str
    userId: int
    blockId: str
    languageId: str
    sourceCode: str
    isCompleted: bool
    executionCount: int
    successfulExecutions: int
    lastExecutionId: Optional[str]
    createdAt: datetime
    updatedAt: datetime 