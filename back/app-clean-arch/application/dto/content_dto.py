"""DTO для работы с контентом"""

from typing import List, Optional

from pydantic import BaseModel

from .base_dto import PaginatedResponse, StringIdentifiedResponse


class ContentFileResponse(StringIdentifiedResponse):
    """Ответ с информацией о файле контента"""

    webdavPath: str
    mainCategory: str
    subCategory: str
    lastFileHash: Optional[str] = None


class ContentBlockResponse(StringIdentifiedResponse):
    """Ответ с информацией о блоке контента"""

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

    # Связанные данные
    file: Optional[ContentFileResponse] = None


class ContentBlockWithProgressResponse(ContentBlockResponse):
    """Ответ с информацией о блоке контента и прогрессе пользователя"""

    userProgress: int = 0


class UserContentProgressResponse(StringIdentifiedResponse):
    """Ответ с информацией о прогрессе пользователя"""

    userId: int
    blockId: str
    solvedCount: int


class ProgressAction(BaseModel):
    """Действие для обновления прогресса"""

    action: str  # "increment" или "decrement"


# Типизированные пагинированные ответы
ContentBlocksListResponse = PaginatedResponse[ContentBlockResponse]
ContentFilesListResponse = PaginatedResponse[ContentFileResponse]


class ContentCategoriesResponse(BaseModel):
    """Ответ со списком категорий"""

    categories: List[str]

    @classmethod
    def create(cls, categories: List[str]) -> "ContentCategoriesResponse":
        """Создание ответа с категориями"""
        return cls(categories=categories)


class ContentSubcategoriesResponse(BaseModel):
    """Ответ со списком подкатегорий"""

    subcategories: List[str]

    @classmethod
    def create(cls, subcategories: List[str]) -> "ContentSubcategoriesResponse":
        """Создание ответа с подкатегориями"""
        return cls(subcategories=subcategories)
