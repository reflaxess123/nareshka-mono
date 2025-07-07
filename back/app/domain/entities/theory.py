"""Сущности для теоретических карточек"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from dataclasses import dataclass, field

from .enums import CardState


@dataclass
class TheoryCard:
    """Доменная сущность теоретической карточки"""
    id: str
    ankiGuid: str
    cardType: str
    deck: str
    category: str
    subCategory: Optional[str]
    questionBlock: str
    answerBlock: str
    tags: List[str] = field(default_factory=list)
    orderIndex: int = 0
    createdAt: datetime = None
    updatedAt: datetime = None


@dataclass
class UserTheoryProgress:
    """Доменная сущность прогресса пользователя по теоретической карточке"""
    id: str
    userId: int
    cardId: str
    solvedCount: int
    easeFactor: Decimal
    interval: int
    dueDate: Optional[datetime]
    reviewCount: int
    lapseCount: int
    cardState: CardState
    learningStep: int
    lastReviewDate: Optional[datetime]
    createdAt: datetime
    updatedAt: datetime 