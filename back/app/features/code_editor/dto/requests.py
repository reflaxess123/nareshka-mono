"""Request DTOs для code_editor feature"""

from typing import Optional

from pydantic import BaseModel, Field

from app.shared.entities.enums import CodeLanguage


class CodeExecutionRequest(BaseModel):
    """Запрос на выполнение кода"""

    sourceCode: str = Field(..., description="Исходный код для выполнения")
    language: str = Field(..., description="Язык программирования")
    stdin: Optional[str] = Field(None, description="Входные данные для программы")
    blockId: Optional[str] = Field(None, description="ID блока контента")


class UserCodeSolutionCreateRequest(BaseModel):
    """Запрос на создание решения пользователя"""

    blockId: str = Field(..., description="ID блока контента")
    language: CodeLanguage = Field(..., description="Язык программирования")
    sourceCode: str = Field(..., description="Исходный код решения")
    isCompleted: bool = Field(default=False, description="Решение завершено")


class UserCodeSolutionUpdateRequest(BaseModel):
    """Запрос на обновление решения пользователя"""

    sourceCode: Optional[str] = Field(None, description="Новый исходный код")
    isCompleted: Optional[bool] = Field(None, description="Статус завершенности")


class ValidationRequest(BaseModel):
    """Запрос на валидацию решения"""

    sourceCode: str = Field(..., description="Исходный код для валидации")
    language: CodeLanguage = Field(..., description="Язык программирования")
    stdin: Optional[str] = Field(None, description="Входные данные для тестов")


class TestCaseCreateRequest(BaseModel):
    """Запрос на создание тест-кейса"""

    blockId: str = Field(..., description="ID блока контента")
    name: str = Field(..., description="Название тест-кейса")
    description: Optional[str] = Field(None, description="Описание тест-кейса")
    input: str = Field(default="", description="Входные данные")
    expectedOutput: str = Field(..., description="Ожидаемый результат")
    isPublic: bool = Field(default=True, description="Публичный тест-кейс")
    difficulty: str = Field(default="BASIC", description="Уровень сложности")
    weight: float = Field(default=1.0, description="Вес тест-кейса")
    timeoutSeconds: int = Field(default=5, description="Таймаут выполнения")
    isActive: bool = Field(default=True, description="Активен ли тест-кейс")
    orderIndex: int = Field(default=0, description="Порядок выполнения")
