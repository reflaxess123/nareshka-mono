"""DTO для работы с контентом"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class ContentFileResponse(BaseModel):
    """Ответ с информацией о файле контента"""
    id: str
    webdavPath: str
    mainCategory: str
    subCategory: str
    lastFileHash: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        from_attributes = True


class ContentBlockResponse(BaseModel):
    """Ответ с информацией о блоке контента"""
    id: str
    fileId: str
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
    companies: List[str] = []
    rawBlockContentHash: Optional[str] = None
    
    createdAt: datetime
    updatedAt: datetime
    
    # Связанные данные
    file: Optional[ContentFileResponse] = None
    
    class Config:
        from_attributes = True


class ContentBlockWithProgressResponse(ContentBlockResponse):
    """Ответ с информацией о блоке контента и прогрессе пользователя"""
    userProgress: int = 0


class UserContentProgressResponse(BaseModel):
    """Ответ с информацией о прогрессе пользователя"""
    id: str
    userId: int
    blockId: str
    solvedCount: int
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        from_attributes = True


class ProgressAction(BaseModel):
    """Действие для обновления прогресса"""
    action: str  # "increment" или "decrement"


class ContentBlocksListResponse(BaseModel):
    """Ответ со списком блоков контента"""
    blocks: List[ContentBlockResponse]
    total: int
    page: int
    limit: int
    totalPages: int
    
    @classmethod
    def create(cls, blocks: List[ContentBlockResponse], total: int, page: int, limit: int):
        """Создание ответа со списком блоков"""
        total_pages = (total + limit - 1) // limit
        return cls(
            blocks=blocks,
            total=total,
            page=page,
            limit=limit,
            totalPages=total_pages
        )


class ContentFilesListResponse(BaseModel):
    """Ответ со списком файлов контента"""
    files: List[ContentFileResponse]
    total: int
    page: int
    limit: int
    totalPages: int
    
    @classmethod
    def create(cls, files: List[ContentFileResponse], total: int, page: int, limit: int):
        """Создание ответа со списком файлов"""
        total_pages = (total + limit - 1) // limit
        return cls(
            files=files,
            total=total,
            page=page,
            limit=limit,
            totalPages=total_pages
        )


class ContentCategoriesResponse(BaseModel):
    """Ответ со списком категорий"""
    categories: List[str]


class ContentSubcategoriesResponse(BaseModel):
    """Ответ со списком подкатегорий"""
    subcategories: List[str] 