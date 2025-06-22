from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, EmailStr

from .models import CardState, CodeLanguage, ExecutionStatus, UserRole, ProgressStatus


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    role: UserRole
    createdAt: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class ContentFileBase(BaseModel):
    webdavPath: str
    mainCategory: str
    subCategory: str
    lastFileHash: Optional[str] = None


class ContentFileCreate(ContentFileBase):
    pass


class ContentFileResponse(ContentFileBase):
    id: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class ContentBlockBase(BaseModel):
    pathTitles: List[str]
    blockTitle: str
    blockLevel: int
    orderInFile: int
    textContent: Optional[str] = None
    codeContent: Optional[str] = None
    codeLanguage: Optional[str] = None
    isCodeFoldable: bool = False
    codeFoldTitle: Optional[str] = None
    extractedUrls: List[str] = []
    rawBlockContentHash: Optional[str] = None


class ContentBlockCreate(ContentBlockBase):
    fileId: str


class ContentBlockResponse(ContentBlockBase):
    id: str
    fileId: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class UserContentProgressBase(BaseModel):
    solvedCount: int = 0


class UserContentProgressCreate(UserContentProgressBase):
    userId: int
    blockId: str


class UserContentProgressResponse(UserContentProgressBase):
    id: str
    userId: int
    blockId: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class TheoryCardBase(BaseModel):
    ankiGuid: str
    cardType: str
    deck: str
    category: str
    subCategory: Optional[str] = None
    questionBlock: str
    answerBlock: str
    tags: List[str] = []
    orderIndex: int = 0


class TheoryCardCreate(TheoryCardBase):
    pass


class TheoryCardResponse(TheoryCardBase):
    id: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class UserTheoryProgressBase(BaseModel):
    solvedCount: int = 0
    easeFactor: Decimal = Decimal("2.50")
    interval: int = 1
    dueDate: Optional[datetime] = None
    reviewCount: int = 0
    lapseCount: int = 0
    cardState: CardState = CardState.NEW
    learningStep: int = 0
    lastReviewDate: Optional[datetime] = None


class UserTheoryProgressCreate(UserTheoryProgressBase):
    userId: int
    cardId: str


class UserTheoryProgressResponse(UserTheoryProgressBase):
    id: str
    userId: int
    cardId: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str


class UserStatsResponse(BaseModel):
    totalBlocks: int
    completedBlocks: int
    totalCards: int
    completedCards: int
    categories: List[str]

    class Config:
        from_attributes = True


class SupportedLanguagePublic(BaseModel):
    id: str
    name: str
    language: CodeLanguage
    version: str
    fileExtension: str
    timeoutSeconds: int
    memoryLimitMB: int
    isEnabled: bool

    class Config:
        from_attributes = True


class CodeExecutionRequest(BaseModel):
    sourceCode: str
    language: str
    stdin: Optional[str] = None
    blockId: Optional[str] = None


class CodeExecutionResponse(BaseModel):
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
    memoryUsedMB: Optional[int] = None
    containerLogs: Optional[str] = None
    errorMessage: Optional[str] = None
    createdAt: datetime
    completedAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserCodeSolutionCreate(BaseModel):
    blockId: str
    language: CodeLanguage
    sourceCode: str
    isCompleted: bool = False


class UserCodeSolutionUpdate(BaseModel):
    sourceCode: Optional[str] = None
    isCompleted: Optional[bool] = None


class UserCodeSolutionResponse(BaseModel):
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

    class Config:
        from_attributes = True


class LanguageStat(BaseModel):
    language: CodeLanguage
    name: str
    executions: int


class ExecutionStats(BaseModel):
    totalExecutions: int
    successfulExecutions: int
    averageExecutionTime: float
    languageStats: List[LanguageStat]


class UserCategoryProgressBase(BaseModel):
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


class UserCategoryProgressCreate(UserCategoryProgressBase):
    userId: int


class UserCategoryProgressResponse(UserCategoryProgressBase):
    id: str
    userId: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class TaskAttemptBase(BaseModel):
    sourceCode: str
    language: str
    isSuccessful: bool = False
    executionTimeMs: Optional[int] = None
    memoryUsedMB: Optional[float] = None
    errorMessage: Optional[str] = None
    stderr: Optional[str] = None
    durationMinutes: Optional[int] = None


class TaskAttemptCreate(TaskAttemptBase):
    userId: int
    blockId: str


class TaskAttemptResponse(TaskAttemptBase):
    id: str
    userId: int
    blockId: str
    attemptNumber: int
    createdAt: datetime

    class Config:
        from_attributes = True


class TaskSolutionBase(BaseModel):
    finalCode: str
    language: str
    totalAttempts: int
    timeToSolveMinutes: int
    firstAttempt: datetime


class TaskSolutionCreate(TaskSolutionBase):
    userId: int
    blockId: str


class TaskSolutionResponse(TaskSolutionBase):
    id: str
    userId: int
    blockId: str
    solvedAt: datetime
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class LearningPathBase(BaseModel):
    name: str
    description: Optional[str] = None
    blockIds: List[str]
    prerequisites: List[str] = []
    difficulty: Optional[str] = None
    estimatedHours: Optional[int] = None
    tags: List[str] = []
    isActive: bool = True
    orderIndex: int = 0


class LearningPathCreate(LearningPathBase):
    pass


class LearningPathResponse(LearningPathBase):
    id: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class UserPathProgressBase(BaseModel):
    currentBlockIndex: int = 0
    completedBlockIds: List[str] = []
    isCompleted: bool = False
    startedAt: datetime
    completedAt: Optional[datetime] = None
    lastActivity: Optional[datetime] = None


class UserPathProgressCreate(UserPathProgressBase):
    userId: int
    pathId: str


class UserPathProgressResponse(UserPathProgressBase):
    id: str
    userId: int
    pathId: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class CategoryProgressSummary(BaseModel):
    mainCategory: str
    subCategory: Optional[str] = None
    totalTasks: int
    completedTasks: int
    attemptedTasks: int
    completionRate: float
    averageAttempts: float
    totalTimeSpent: int
    lastActivity: Optional[datetime]
    status: str


class UserDetailedProgressResponse(BaseModel):
    userId: int
    totalTasksSolved: int
    lastActivityDate: Optional[datetime]
    
    overallStats: dict
    
    categoryProgress: List[CategoryProgressSummary]
    
    recentAttempts: List[TaskAttemptResponse]
    
    recentSolutions: List[TaskSolutionResponse]
    
    learningPaths: List[UserPathProgressResponse]

    class Config:
        from_attributes = True


class ProgressAnalytics(BaseModel):
    totalUsers: int
    activeUsers: int  
    totalTasksSolved: int
    averageTasksPerUser: float
    mostPopularCategories: List[dict]
    strugglingAreas: List[dict]
    
    class Config:
        from_attributes = True
