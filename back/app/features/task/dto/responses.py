"""DTO ответов для работы с заданиями"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class FileResponse(BaseModel):
    """Ответ с информацией о файле"""

    id: str
    webdavPath: str
    mainCategory: str
    subCategory: Optional[str] = None

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    """Ответ с информацией о задании"""

    id: str
    type: str
    title: str
    description: Optional[str] = None
    category: str
    subCategory: Optional[str] = None

    # Поля для content_block
    fileId: Optional[str] = None
    file: Optional[FileResponse] = None
    pathTitles: Optional[List[str]] = None
    blockLevel: Optional[int] = None
    orderInFile: Optional[int] = None
    textContent: Optional[str] = None
    codeContent: Optional[str] = None
    codeLanguage: Optional[str] = None
    isCodeFoldable: Optional[bool] = None
    codeFoldTitle: Optional[str] = None
    extractedUrls: Optional[List[str]] = None
    companies: Optional[List[str]] = None

    # Поля для theory_quiz
    questionBlock: Optional[str] = None
    answerBlock: Optional[str] = None
    tags: Optional[List[str]] = None
    orderIndex: Optional[int] = None

    # Прогресс пользователя
    currentUserSolvedCount: int = 0

    # Метаданные
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class TasksListResponse(BaseModel):
    """Ответ со списком заданий"""

    data: List[TaskResponse]
    pagination: Dict[str, Any]

    @classmethod
    def create(cls, tasks: List[TaskResponse], total: int, page: int, limit: int):
        pagination = {
            "page": page,
            "limit": limit,
            "total": total,
            "totalPages": (total + limit - 1) // limit,
            "hasNext": page * limit < total,
            "hasPrev": page > 1,
        }

        return cls(data=tasks, pagination=pagination)


class TaskCategoryResponse(BaseModel):
    """Ответ с информацией о категории заданий"""

    name: str
    subCategories: List[str] = []
    totalCount: int
    contentBlockCount: int = 0
    theoryQuizCount: int = 0

    class Config:
        from_attributes = True


class TaskCategoriesResponse(BaseModel):
    """Ответ со списком категорий заданий"""

    categories: List[TaskCategoryResponse]

    class Config:
        from_attributes = True


class TaskCompanyResponse(BaseModel):
    """Ответ с информацией о компании"""

    name: str
    count: int

    class Config:
        from_attributes = True


class TaskCompaniesResponse(BaseModel):
    """Ответ со списком компаний"""

    companies: List[TaskCompanyResponse]

    class Config:
        from_attributes = True


class TaskAttemptResponse(BaseModel):
    """Ответ с информацией о попытке решения"""

    id: str
    userId: int
    blockId: str
    sourceCode: str
    language: str
    isSuccessful: bool
    attemptNumber: int
    executionTimeMs: Optional[int] = None
    memoryUsedMB: Optional[float] = None
    errorMessage: Optional[str] = None
    stderr: Optional[str] = None
    durationMinutes: Optional[int] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class TaskSolutionResponse(BaseModel):
    """Ответ с информацией о решении задачи"""

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

    class Config:
        from_attributes = True
