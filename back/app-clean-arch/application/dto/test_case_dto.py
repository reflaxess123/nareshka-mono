"""DTO для работы с тест-кейсами"""

from typing import List, Optional

from pydantic import BaseModel


class TestCaseAIGenerate(BaseModel):
    """DTO для генерации тест-кейсов через AI"""

    blockId: str
    count: int = 5
    difficulty: str = "BASIC"
    includeEdgeCases: bool = True
    includeErrorCases: bool = False


class TestCaseResponse(BaseModel):
    """DTO для ответа с тест-кейсом"""

    id: str
    blockId: str
    name: str
    description: Optional[str]
    input: str
    expectedOutput: str
    isPublic: bool
    difficulty: str
    weight: float
    timeoutSeconds: int
    isActive: bool
    orderIndex: int
    isAIGenerated: bool
    executionCount: int
    passRate: float


class TestCaseCreateRequest(BaseModel):
    """DTO для создания тест-кейса"""

    blockId: str
    name: str
    description: Optional[str] = None
    input: str = ""
    expectedOutput: str
    isPublic: bool = True
    difficulty: str = "BASIC"
    weight: float = 1.0
    timeoutSeconds: int = 30


class ValidationRequestDTO(BaseModel):
    """DTO для запроса валидации"""

    sourceCode: str
    language: str


class ValidationResultDTO(BaseModel):
    """DTO для результата валидации"""

    passed: bool
    totalTests: int
    passedTests: int
    failedTests: int
    results: List[dict]
