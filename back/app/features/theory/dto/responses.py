"""DTO ответов для работы с теоретическими карточками"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.shared.models.enums import CardState


class TheoryCardResponse(BaseModel):
    """Ответ с информацией о теоретической карточке"""

    id: str
    ankiGuid: str
    cardType: str
    deck: str
    category: str
    subCategory: Optional[str] = None
    questionBlock: str
    answerBlock: str
    tags: List[str] = []
    orderIndex: int = 0
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
        populate_by_name = True

    def model_dump(self, **kwargs):
        """Переопределяем model_dump для возврата camelCase"""
        return super().model_dump(**kwargs)


class UserTheoryProgressResponse(BaseModel):
    """Ответ с информацией о прогрессе изучения карточки"""

    id: str
    userId: int
    cardId: str
    solvedCount: int = 0
    easeFactor: Decimal = Decimal("2.50")
    interval: int = 1
    dueDate: Optional[datetime] = None
    reviewCount: int = 0
    lapseCount: int = 0
    cardState: CardState = CardState.NEW
    learningStep: int = 0
    lastReviewDate: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class TheoryCardWithProgressResponse(TheoryCardResponse):
    """Ответ с информацией о теоретической карточке и прогрессе пользователя"""

    progress: Optional[UserTheoryProgressResponse] = None


class TheoryCardsListResponse(BaseModel):
    """Ответ со списком теоретических карточек"""

    cards: List[TheoryCardResponse]
    pagination: Dict[str, Any]

    @classmethod
    def create(cls, cards: List[TheoryCardResponse], total: int, page: int, limit: int):
        pagination = {
            "page": page,
            "limit": limit,
            "total": total,
            "totalPages": (total + limit - 1) // limit,
            "hasNext": page * limit < total,
            "hasPrev": page > 1,
        }

        return cls(cards=cards, pagination=pagination)


class TheoryCategoriesResponse(BaseModel):
    """Ответ со списком категорий"""

    categories: List[Dict[str, Any]]

    class Config:
        from_attributes = True


class TheorySubcategoriesResponse(BaseModel):
    """Ответ со списком подкатегорий"""

    subcategories: List[str]

    class Config:
        from_attributes = True


class TheoryStatsResponse(BaseModel):
    """Ответ со статистикой изучения теории"""

    totalCards: int
    studiedCards: int
    dueCards: int
    averageEaseFactor: float
    studyProgress: float

    class Config:
        from_attributes = True


class DueCardsResponse(BaseModel):
    """Ответ с карточками для повторения"""

    cards: List[TheoryCardResponse]
    total: int

    class Config:
        from_attributes = True
