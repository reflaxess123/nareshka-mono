"""DTO ответов для работы с теоретическими карточками"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.shared.entities.enums import CardState


class TheoryCardResponse(BaseModel):
    """Ответ с информацией о теоретической карточке"""

    id: str
    ankiGuid: str = Field(alias="anki_guid")
    cardType: str = Field(alias="card_type")
    deck: str
    category: str
    subCategory: Optional[str] = Field(alias="sub_category", default=None)
    questionBlock: str = Field(alias="question_block")
    answerBlock: str = Field(alias="answer_block")
    tags: List[str] = []
    orderIndex: int = Field(alias="order_index", default=0)
    createdAt: datetime = Field(alias="created_at")
    updatedAt: datetime = Field(alias="updated_at")

    class Config:
        from_attributes = True
        populate_by_name = True


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
        
        return cls(
            cards=cards,
            pagination=pagination
        )


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


