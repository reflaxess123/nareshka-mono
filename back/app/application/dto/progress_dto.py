from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


# TaskAttempt DTOs
class TaskAttemptCreateDTO(BaseModel):
    userId: int
    blockId: str
    sourceCode: str
    language: str
    isSuccessful: bool = False
    executionTimeMs: Optional[int] = None
    memoryUsedMB: Optional[float] = None
    errorMessage: Optional[str] = None
    stderr: Optional[str] = None
    durationMinutes: Optional[int] = None


class TaskAttemptResponseDTO(BaseModel):
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


# TaskSolution DTOs
class TaskSolutionResponseDTO(BaseModel):
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


# Progress DTOs
class CategoryProgressSummaryDTO(BaseModel):
    mainCategory: str
    subCategory: Optional[str] = None
    totalTasks: int
    completedTasks: int
    completionRate: float
    status: str  # not_started, in_progress, completed


class SubCategoryProgressDTO(BaseModel):
    subCategory: str
    totalTasks: int
    completedTasks: int
    completionRate: float
    status: str  # not_started, in_progress, completed


class GroupedCategoryProgressDTO(BaseModel):
    mainCategory: str
    totalTasks: int
    completedTasks: int
    completionRate: float
    status: str  # not_started, in_progress, completed
    subCategories: List[SubCategoryProgressDTO]


class SimplifiedOverallStatsDTO(BaseModel):
    totalTasksSolved: int
    totalTasksAvailable: int
    completionRate: float


class RecentActivityItemDTO(BaseModel):
    id: str
    blockId: str
    blockTitle: str
    category: str
    subCategory: Optional[str]
    isSuccessful: bool
    activityType: str  # "attempt" или "solution"
    timestamp: datetime


class UserDetailedProgressResponseDTO(BaseModel):
    userId: int
    lastActivityDate: Optional[datetime]
    overallStats: SimplifiedOverallStatsDTO
    categoryProgress: List[CategoryProgressSummaryDTO]
    groupedCategoryProgress: List[GroupedCategoryProgressDTO]
    recentActivity: List[RecentActivityItemDTO]


class ProgressAnalyticsDTO(BaseModel):
    totalUsers: int
    activeUsers: int  
    totalTasksSolved: int
    averageTasksPerUser: float
    mostPopularCategories: List[Dict[str, Any]]
    strugglingAreas: List[Dict[str, Any]]


# Learning Path DTOs
class LearningPathResponseDTO(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    blockIds: List[str]
    prerequisites: List[str] = []
    difficulty: Optional[str] = None
    estimatedHours: Optional[int] = None
    tags: List[str] = []
    isActive: bool = True
    orderIndex: int = 0
    createdAt: datetime
    updatedAt: datetime


class UserPathProgressResponseDTO(BaseModel):
    id: str
    userId: int
    pathId: str
    currentBlockIndex: int = 0
    completedBlockIds: List[str] = []
    isCompleted: bool = False
    startedAt: datetime
    completedAt: Optional[datetime] = None
    lastActivity: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime


# UserCategoryProgress DTOs
class UserCategoryProgressResponseDTO(BaseModel):
    id: str
    userId: int
    mainCategory: str
    subCategory: Optional[str] = None
    totalTasks: int = 0
    completedTasks: int = 0
    attemptedTasks: int = 0
    averageAttempts: Decimal = Decimal("0.0")
    totalTimeSpentMinutes: int = 0
    successRate: Decimal = Decimal("0.0")
    firstAttempt: Optional[datetime] = None
    lastActivity: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime


# Test Case DTOs
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


class TestValidationResultResponseDTO(BaseModel):
    id: str
    testCaseId: str
    attemptId: str
    passed: bool
    actualOutput: Optional[str] = None
    executionTimeMs: Optional[int] = None
    errorMessage: Optional[str] = None
    outputMatch: bool = False
    outputSimilarity: float = 0.0
    createdAt: datetime 