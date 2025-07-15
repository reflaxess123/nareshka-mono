"""
Content Feature Response DTOs

Модели ответов для API endpoints контента.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

from app.shared.dto import StringIdentifiedResponse, PaginatedResponse


class ContentFileResponse(StringIdentifiedResponse):
    """Ответ с информацией о файле контента"""

    webdavPath: str = Field(..., description="Путь к файлу в WebDAV системе")
    mainCategory: str = Field(..., description="Основная категория контента")
    subCategory: str = Field(..., description="Подкатегория контента")
    lastFileHash: Optional[str] = Field(None, description="Хэш последней версии файла")


class ContentBlockResponse(StringIdentifiedResponse):
    """Ответ с информацией о блоке контента"""

    fileId: str = Field(..., description="ID файла, к которому принадлежит блок")
    pathTitles: List[str] = Field(..., description="Путь заголовков для навигации")
    blockTitle: str = Field(..., description="Заголовок блока")
    blockLevel: int = Field(..., description="Уровень вложенности блока")
    orderInFile: int = Field(..., description="Порядок блока в файле")

    # Content data
    textContent: Optional[str] = Field(None, description="Текстовое содержимое блока")
    codeContent: Optional[str] = Field(None, description="Код в блоке")
    codeLanguage: Optional[str] = Field(None, description="Язык программирования кода")
    isCodeFoldable: bool = Field(False, description="Можно ли свернуть код")
    codeFoldTitle: Optional[str] = Field(None, description="Заголовок для свернутого кода")

    # Metadata
    extractedUrls: List[str] = Field(default_factory=list, description="Извлеченные URL")
    companies: List[str] = Field(default_factory=list, description="Связанные компании")
    rawBlockContentHash: Optional[str] = Field(None, description="Хэш содержимого")

    # Related data
    file: Optional[ContentFileResponse] = Field(None, description="Информация о файле")


class ContentBlockWithProgressResponse(ContentBlockResponse):
    """Ответ с информацией о блоке контента и прогрессе пользователя"""

    userProgress: int = Field(0, description="Прогресс пользователя по блоку")


class UserContentProgressResponse(StringIdentifiedResponse):
    """Ответ с информацией о прогрессе пользователя"""

    userId: int = Field(..., description="ID пользователя")
    blockId: str = Field(..., description="ID блока контента")
    solvedCount: int = Field(..., description="Количество решенных задач в блоке")


class ContentCategoriesResponse(BaseModel):
    """Ответ со списком категорий контента"""

    categories: List[str] = Field(..., description="Список основных категорий")

    @classmethod
    def create(cls, categories: List[str]) -> "ContentCategoriesResponse":
        """Создание ответа с категориями"""
        return cls(categories=categories)


class ContentSubcategoriesResponse(BaseModel):
    """Ответ со списком подкатегорий контента"""

    subcategories: List[str] = Field(..., description="Список подкатегорий")

    @classmethod
    def create(cls, subcategories: List[str]) -> "ContentSubcategoriesResponse":
        """Создание ответа с подкатегориями"""
        return cls(subcategories=subcategories)


# Типизированные пагинированные ответы
ContentBlocksListResponse = PaginatedResponse[ContentBlockResponse]
ContentFilesListResponse = PaginatedResponse[ContentFileResponse] 


