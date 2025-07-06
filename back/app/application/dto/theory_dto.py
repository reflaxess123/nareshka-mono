"""DTO для работы с теоретическими карточками"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from ...domain.entities.enums import CardState


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


class ProgressAction(BaseModel):
    """Действие для обновления прогресса"""
    action: str  # "increment" или "decrement"


class ReviewRating(BaseModel):
    """Оценка повторения карточки"""
    rating: str  # "again", "hard", "good", "easy"


class TheoryCardsListResponse(BaseModel):
    """Ответ со списком теоретических карточек"""
    cards: List[TheoryCardResponse]
    pagination: Dict[str, Any]
    
    @classmethod
    def create(cls, cards: List[TheoryCardResponse], total: int, page: int, limit: int):
        """Создание ответа со списком карточек"""
        total_pages = (total + limit - 1) // limit
        return cls(
            cards=cards,
            pagination={
                "page": page,
                "limit": limit,
                "totalCount": total,
                "totalPages": total_pages,
                "hasNextPage": page < total_pages,
                "hasPrevPage": page > 1
            }
        )


class TheoryCategoryResponse(BaseModel):
    """Ответ с информацией о категории"""
    name: str
    subCategories: List[Dict[str, Any]] = []
    totalCards: int = 0


class TheoryCategoriesResponse(BaseModel):
    """Ответ со списком категорий"""
    categories: List[Dict[str, Any]]


class TheorySubcategoriesResponse(BaseModel):
    """Ответ со списком подкатегорий"""
    subcategories: List[str]


class TheoryStatsResponse(BaseModel):
    """Ответ со статистикой изучения теории"""
    totalCards: int
    studiedCards: int
    dueCards: int
    averageEaseFactor: float
    studyProgress: float


class CardStatsResponse(BaseModel):
    """Ответ со статистикой по конкретной карточке"""
    cardId: str
    totalReviews: int
    correctReviews: int
    lapseCount: int
    averageInterval: float
    lastReview: Optional[datetime] = None
    nextReview: Optional[datetime] = None
    currentState: CardState


class CardIntervalsResponse(BaseModel):
    """Ответ с интервалами повторения карточки"""
    cardId: str
    intervals: List[Dict[str, Any]]


class DueCardsResponse(BaseModel):
    """Ответ с карточками для повторения"""
    cards: List[TheoryCardResponse]
    total: int 