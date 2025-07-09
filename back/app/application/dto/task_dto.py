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
        return cls(
            id=task.id,
            type=task.item_type,
            title=task.title,
            description=task.description,
            category=task.main_category,
            subCategory=task.sub_category,
            
            # Базовые поля для всех типов
            companies=task.companies,
            tags=task.tags,
            codeContent=task.code_content,
            codeLanguage=task.code_language.value if task.code_language else None,
            orderInFile=task.order_in_file,
            
            # Поля для content_block (могут быть пустыми для theory_quiz)
            fileId=None,  # Не доступно в модели Task
            file=None,
            pathTitles=None,  # Не доступно в модели Task
            blockLevel=None,  # Не доступно в модели Task
            textContent=task.description,  # Используем description
            isCodeFoldable=None,  # Не доступно в модели Task
            codeFoldTitle=None,  # Не доступно в модели Task
            extractedUrls=None,  # Не доступно в модели Task
            
            # Поля для theory_quiz
            questionBlock=task.title if task.item_type == "theory_quiz" else None,
            answerBlock=task.description if task.item_type == "theory_quiz" else None,
            orderIndex=task.order_in_file,
            
            # Прогресс пользователя
            currentUserSolvedCount=1 if task.is_solved else 0,
            
            # Метаданные
            createdAt=task.created_at,
            updatedAt=task.updated_at
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
    subCategories: List[str] = []
    totalCount: int
    contentBlockCount: int = 0
    theoryQuizCount: int = 0
    
    @classmethod
    def from_domain(cls, category: TaskCategory) -> 'TaskCategoryResponse':
        """Создание DTO из доменной модели"""
        return cls(
            name=category.main_category,
            subCategories=[category.sub_category] if category.sub_category else [],
            totalCount=category.task_count,
            contentBlockCount=category.task_count,  # Для простоты
            theoryQuizCount=0  # Для простоты
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
            name=company.company,
            count=company.task_count
        )


class TaskCompaniesResponse(BaseModel):
    """Ответ со списком компаний"""
    companies: List[TaskCompanyResponse]
    
    def __init__(self, companies: List[TaskCompany], **data):
        company_responses = [
            TaskCompanyResponse.from_domain(comp) for comp in companies
        ]
        super().__init__(companies=company_responses, **data) 