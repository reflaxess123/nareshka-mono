from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from enum import Enum

from .enums import ProgressStatus


class CardState(str, Enum):
    NEW = "NEW"
    LEARNING = "LEARNING"
    REVIEW = "REVIEW"
    RELEARNING = "RELEARNING"


@dataclass
class TaskAttempt:
    id: str
    userId: int
    blockId: str
    sourceCode: str
    language: str
    isSuccessful: bool
    attemptNumber: int
    createdAt: datetime
    
    executionTimeMs: Optional[int] = None
    memoryUsedMB: Optional[float] = None
    errorMessage: Optional[str] = None
    stderr: Optional[str] = None
    durationMinutes: Optional[int] = None


@dataclass
class TaskSolution:
    id: str
    userId: int
    blockId: str
    finalCode: str
    language: str
    totalAttempts: int
    timeToSolveMinutes: int
    firstAttempt: datetime
    solvedAt: datetime
    createdAt: datetime
    updatedAt: datetime


@dataclass
class UserCategoryProgress:
    id: str
    userId: int
    category: str
    completedTasks: int
    totalTasks: int
    completedTheory: int
    totalTheory: int
    completedContent: int
    totalContent: int
    createdAt: datetime
    updatedAt: datetime


@dataclass
class LearningPath:
    id: str
    name: str
    description: Optional[str]
    difficulty: Optional[str]
    estimatedTime: Optional[int]
    isActive: bool
    createdAt: datetime
    updatedAt: datetime


@dataclass
class UserPathProgress:
    id: str
    userId: int
    pathId: str
    currentStep: int
    completedSteps: int
    totalSteps: int
    status: ProgressStatus
    startedAt: Optional[datetime]
    completedAt: Optional[datetime]
    createdAt: datetime
    updatedAt: datetime


@dataclass
class TestCase:
    id: str
    blockId: str
    name: str
    expectedOutput: str
    isPublic: bool
    difficulty: str
    weight: float
    timeoutSeconds: int
    isActive: bool
    orderIndex: int
    isAIGenerated: bool
    executionCount: int
    passRate: float
    createdAt: datetime
    updatedAt: datetime
    
    description: Optional[str] = None
    input: str = ""
    generationPrompt: Optional[str] = None
    generatedAt: Optional[datetime] = None
    generationModel: Optional[str] = None


@dataclass
class TestValidationResult:
    id: str
    testCaseId: str
    attemptId: str
    passed: bool
    outputMatch: bool
    outputSimilarity: float
    createdAt: datetime
    
    actualOutput: Optional[str] = None
    executionTimeMs: Optional[int] = None
    errorMessage: Optional[str] = None 