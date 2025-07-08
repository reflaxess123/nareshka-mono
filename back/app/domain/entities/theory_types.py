"""Theory types для внутреннего использования в services и repositories."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class TheoryCard(BaseModel):
    """Карточка теории"""
    id: str
    anki_guid: Optional[str] = None
    card_type: str
    deck: str
    category: str
    sub_category: Optional[str] = None
    question_block: str
    answer_block: str
    tags: List[str] = []
    order_index: int = 0
    created_at: datetime
    updated_at: datetime


class UserTheoryProgress(BaseModel):
    """Прогресс пользователя по карточке теории"""
    id: str
    user_id: int
    card_id: str
    review_count: int = 0
    last_reviewed_at: Optional[datetime] = None
    card_state: str = "new"  # new, learning, review, graduated
    ease_factor: float = 2.5
    interval_days: int = 1
    due_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime 