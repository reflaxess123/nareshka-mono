"""Сущности для заданий (объединенные content blocks и quiz карточки)"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass

from .content import ContentBlock, UserContentProgress
from .theory import TheoryCard, UserTheoryProgress


class TaskType(str, Enum):
    """Тип задания"""
    CONTENT_BLOCK = "content_block"
    THEORY_QUIZ = "theory_quiz"


@dataclass
class Task:
    """Объединенная сущность для заданий"""
    # Обязательные поля (без значений по умолчанию)
    id: str
    type: TaskType
    title: str
    category: str
    createdAt: datetime
    updatedAt: datetime
    
    # Опциональные поля (со значениями по умолчанию)
    description: Optional[str] = None
    subCategory: Optional[str] = None
    
    # Поля для content_block
    fileId: Optional[str] = None
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
    
    @classmethod
    def from_content_block(
        cls, 
        content_block: ContentBlock, 
        progress: Optional[UserContentProgress] = None
    ) -> 'Task':
        """Создание Task из ContentBlock"""
        return cls(
            id=content_block.id,
            type=TaskType.CONTENT_BLOCK,
            title=content_block.blockTitle or "Untitled",
            category=content_block.file.mainCategory if content_block.file else "Unknown",
            createdAt=content_block.createdAt,
            updatedAt=content_block.updatedAt,
            
            description=content_block.textContent,
            subCategory=content_block.file.subCategory if content_block.file else None,
            
            fileId=content_block.fileId,
            pathTitles=content_block.pathTitles,
            blockLevel=content_block.blockLevel,
            orderInFile=content_block.orderInFile,
            textContent=content_block.textContent,
            codeContent=content_block.codeContent,
            codeLanguage=content_block.codeLanguage,
            isCodeFoldable=content_block.isCodeFoldable,
            codeFoldTitle=content_block.codeFoldTitle,
            extractedUrls=content_block.extractedUrls,
            companies=content_block.companies,
            
            currentUserSolvedCount=progress.solvedCount if progress else 0
        )
    
    @classmethod
    def from_theory_card(
        cls, 
        theory_card: TheoryCard, 
        progress: Optional[UserTheoryProgress] = None
    ) -> 'Task':
        """Создание Task из TheoryCard"""
        return cls(
            id=theory_card.id,
            type=TaskType.THEORY_QUIZ,
            title=theory_card.questionBlock[:100] + "..." if len(theory_card.questionBlock) > 100 else theory_card.questionBlock,
            category=theory_card.category,
            createdAt=theory_card.createdAt,
            updatedAt=theory_card.updatedAt,
            
            description=theory_card.answerBlock,
            subCategory=theory_card.subCategory,
            
            questionBlock=theory_card.questionBlock,
            answerBlock=theory_card.answerBlock,
            tags=theory_card.tags,
            orderIndex=theory_card.orderIndex,
            
            currentUserSolvedCount=progress.solvedCount if progress else 0
        )


@dataclass
class TaskCategory:
    """Категория заданий"""
    name: str
    subCategories: List[str]
    totalCount: int
    contentBlockCount: int
    theoryQuizCount: int


@dataclass
class TaskCompany:
    """Компания из заданий"""
    name: str
    count: int 