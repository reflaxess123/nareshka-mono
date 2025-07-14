"""
Content Feature Request DTOs

Модели запросов для API endpoints контента.
"""

from pydantic import BaseModel, Field, validator
from typing import Literal


class ProgressAction(BaseModel):
    """Действие для обновления прогресса пользователя по контенту"""

    action: Literal["increment", "decrement"] = Field(
        ..., 
        description="Тип действия: increment (увеличить) или decrement (уменьшить)"
    )

    @validator("action")
    def validate_action(cls, v):
        """Валидация типа действия"""
        if v not in ["increment", "decrement"]:
            raise ValueError("action must be 'increment' or 'decrement'")
        return v


class ContentBlockCreateRequest(BaseModel):
    """Запрос на создание блока контента (для админки)"""
    
    fileId: str = Field(..., description="ID файла")
    pathTitles: list[str] = Field(..., description="Путь заголовков")
    blockTitle: str = Field(..., min_length=1, description="Заголовок блока")
    blockLevel: int = Field(..., ge=0, description="Уровень вложенности")
    orderInFile: int = Field(..., ge=0, description="Порядок в файле")
    textContent: str | None = Field(None, description="Текстовое содержимое")
    codeContent: str | None = Field(None, description="Код")
    codeLanguage: str | None = Field(None, description="Язык программирования")
    isCodeFoldable: bool = Field(False, description="Можно ли свернуть код")
    codeFoldTitle: str | None = Field(None, description="Заголовок свернутого кода")


class ContentBlockUpdateRequest(BaseModel):
    """Запрос на обновление блока контента (для админки)"""
    
    pathTitles: list[str] | None = Field(None, description="Путь заголовков")
    blockTitle: str | None = Field(None, min_length=1, description="Заголовок блока")
    blockLevel: int | None = Field(None, ge=0, description="Уровень вложенности")
    orderInFile: int | None = Field(None, ge=0, description="Порядок в файле")
    textContent: str | None = Field(None, description="Текстовое содержимое")
    codeContent: str | None = Field(None, description="Код")
    codeLanguage: str | None = Field(None, description="Язык программирования")
    isCodeFoldable: bool | None = Field(None, description="Можно ли свернуть код")
    codeFoldTitle: str | None = Field(None, description="Заголовок свернутого кода")


class ContentFileCreateRequest(BaseModel):
    """Запрос на создание файла контента (для админки)"""
    
    webdavPath: str = Field(..., min_length=1, description="Путь в WebDAV")
    mainCategory: str = Field(..., min_length=1, description="Основная категория")
    subCategory: str = Field(..., min_length=1, description="Подкатегория")


class ContentFileUpdateRequest(BaseModel):
    """Запрос на обновление файла контента (для админки)"""
    
    webdavPath: str | None = Field(None, min_length=1, description="Путь в WebDAV")
    mainCategory: str | None = Field(None, min_length=1, description="Основная категория")
    subCategory: str | None = Field(None, min_length=1, description="Подкатегория") 


