"""Domain entities для TestCase и TestValidationResult"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TestCase:
    """Domain entity для TestCase"""
    id: str
    blockId: str
    
    # Основные данные тест-кейса
    name: str
    description: Optional[str] = None
    input: str = ""
    expectedOutput: str = ""
    
    # Метаданные
    isPublic: bool = True
    difficulty: str = "BASIC"
    weight: float = 1.0
    timeoutSeconds: int = 5
    
    # AI-генерация
    isAIGenerated: bool = False
    generationPrompt: Optional[str] = None
    generatedAt: Optional[datetime] = None
    generationModel: Optional[str] = None
    
    # Статистика использования
    executionCount: int = 0
    passRate: float = 0.0
    
    # Системные поля
    isActive: bool = True
    orderIndex: int = 0
    
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


@dataclass
class TestValidationResult:
    """Domain entity для TestValidationResult"""
    id: str
    testCaseId: str
    attemptId: str
    
    # Результаты выполнения
    passed: bool
    actualOutput: Optional[str] = None
    executionTimeMs: Optional[int] = None
    errorMessage: Optional[str] = None
    
    # Детали сравнения
    outputMatch: bool = False
    outputSimilarity: float = 0.0
    
    createdAt: Optional[datetime] = None 