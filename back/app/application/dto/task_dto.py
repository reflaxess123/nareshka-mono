"""DTO для работы с заданиями"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from ...domain.entities.task_types import Task, TaskType, TaskCategory, TaskCompany


class FileResponse(BaseModel):
    """Ответ с информацией о файле"""
    id: str
    webdavPath: str
    mainCategory: str
    subCategory: Optional[str] = None


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
    createdAt: datetime
    updatedAt: datetime
    
    @classmethod
    def from_domain(cls, task: Task) -> 'TaskResponse':
        """Создание DTO из доменной модели"""
        file_response = None
        if task.type == TaskType.CONTENT_BLOCK and task.fileId:
            # Здесь должна быть логика получения файла, но для упрощения используем None
            file_response = FileResponse(
                id=task.fileId,
                webdavPath="",  # Требует дополнительного запроса
                mainCategory=task.category,
                subCategory=task.subCategory
            )
        
        return cls(
            id=task.id,
            type=task.type.value,
            title=task.title,
            description=task.description,
            category=task.category,
            subCategory=task.subCategory,
            
            fileId=task.fileId,
            file=file_response,
            pathTitles=task.pathTitles,
            blockLevel=task.blockLevel,
            orderInFile=task.orderInFile,
            textContent=task.textContent,
            codeContent=task.codeContent,
            codeLanguage=task.codeLanguage,
            isCodeFoldable=task.isCodeFoldable,
            codeFoldTitle=task.codeFoldTitle,
            extractedUrls=task.extractedUrls,
            companies=task.companies,
            
            questionBlock=task.questionBlock,
            answerBlock=task.answerBlock,
            tags=task.tags,
            orderIndex=task.orderIndex,
            
            currentUserSolvedCount=task.currentUserSolvedCount,
            
            createdAt=task.createdAt,
            updatedAt=task.updatedAt
        )


class TasksListResponse(BaseModel):
    """Ответ со списком заданий"""
    data: List[TaskResponse]
    pagination: Dict[str, Any]
    
    @classmethod
    def create(cls, tasks: List[TaskResponse], total: int, page: int, limit: int):
        """Создание ответа со списком заданий"""
        total_pages = (total + limit - 1) // limit
        return cls(
            data=tasks,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "totalPages": total_pages,
                "hasNext": page < total_pages,
                "hasPrev": page > 1
            }
        )


class TaskCategoryResponse(BaseModel):
    """Ответ с информацией о категории заданий"""
    name: str
    subCategories: List[str]
    totalCount: int
    contentBlockCount: int
    theoryQuizCount: int
    
    @classmethod
    def from_domain(cls, category: TaskCategory) -> 'TaskCategoryResponse':
        """Создание DTO из доменной модели"""
        return cls(
            name=category.name,
            subCategories=category.subCategories,
            totalCount=category.totalCount,
            contentBlockCount=category.contentBlockCount,
            theoryQuizCount=category.theoryQuizCount
        )


class TaskCategoriesResponse(BaseModel):
    """Ответ со списком категорий заданий"""
    categories: List[TaskCategoryResponse]
    
    def __init__(self, categories: List[TaskCategory], **data):
        category_responses = [
            TaskCategoryResponse.from_domain(cat) for cat in categories
        ]
        super().__init__(categories=category_responses, **data)


class TaskCompanyResponse(BaseModel):
    """Ответ с информацией о компании"""
    name: str
    count: int
    
    @classmethod
    def from_domain(cls, company: TaskCompany) -> 'TaskCompanyResponse':
        """Создание DTO из доменной модели"""
        return cls(
            name=company.name,
            count=company.count
        )


class TaskCompaniesResponse(BaseModel):
    """Ответ со списком компаний"""
    companies: List[TaskCompanyResponse]
    
    def __init__(self, companies: List[TaskCompany], **data):
        company_responses = [
            TaskCompanyResponse.from_domain(comp) for comp in companies
        ]
        super().__init__(companies=company_responses, **data) 