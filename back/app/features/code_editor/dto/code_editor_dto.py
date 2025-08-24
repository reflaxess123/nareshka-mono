from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.shared.entities.code_editor_types import TestCaseExecution
from app.shared.entities.enums import CodeLanguage, ExecutionStatus


# SupportedLanguage DTOs
class SupportedLanguageResponseDTO(BaseModel):
    id: str
    name: str
    language: CodeLanguage
    version: str
    fileExtension: str
    timeoutSeconds: int
    memoryLimitMB: int
    isEnabled: bool


# CodeExecution DTOs
class CodeExecutionRequestDTO(BaseModel):
    sourceCode: str
    language: str
    stdin: Optional[str] = None
    blockId: Optional[str] = None


class CodeExecutionResponseDTO(BaseModel):
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


# UserCodeSolution DTOs
class UserCodeSolutionCreateDTO(BaseModel):
    blockId: str
    language: CodeLanguage
    sourceCode: str
    isCompleted: bool = False


class UserCodeSolutionUpdateDTO(BaseModel):
    sourceCode: Optional[str] = None
    isCompleted: Optional[bool] = None


class UserCodeSolutionResponseDTO(BaseModel):
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


# Statistics DTOs
class LanguageStatDTO(BaseModel):
    language: CodeLanguage
    name: str
    executions: int


class ExecutionStatsDTO(BaseModel):
    totalExecutions: int
    successfulExecutions: int
    averageExecutionTime: float
    languageStats: List[Dict[str, Any]]


# TestCase DTOs
class TestCaseResponseDTO(BaseModel):
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


class TestCaseCreateDTO(BaseModel):
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


class TestCaseAIGenerateDTO(BaseModel):
    blockId: str
    count: int = 3
    includeEdgeCases: bool = True
    includeErrorCases: bool = False


# Validation DTOs
class ValidationRequestDTO(BaseModel):
    sourceCode: str
    language: CodeLanguage
    stdin: Optional[str] = None


class TestCaseExecutionDTO(BaseModel):
    testCaseId: str
    testName: str
    input: str
    expectedOutput: str
    actualOutput: str
    passed: bool
    executionTimeMs: Optional[int] = None
    errorMessage: Optional[str] = None


class ValidationResultDTO(BaseModel):
    blockId: str
    sourceCode: str
    language: str
    allTestsPassed: bool
    totalTests: int
    passedTests: int
    score: float
    validatedAt: datetime
    testResults: List[TestCaseExecution]


# Combined response DTOs
class TestCasesResponseDTO(BaseModel):
    blockId: str
    testCases: List[TestCaseResponseDTO]
    totalTests: int
    publicTests: int
    hiddenTests: int
    lastGenerated: Optional[datetime] = None
