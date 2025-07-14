"""DTO запросов для работы с теоретическими карточками"""

from pydantic import BaseModel, Field


class ProgressAction(BaseModel):
    """Действие изменения прогресса карточки"""

    action: str = Field(..., description="increment или decrement")

    class Config:
        from_attributes = True


class ReviewRating(BaseModel):
    """Оценка повторения карточки"""

    rating: str = Field(..., description="again, hard, good, easy")

    class Config:
        from_attributes = True 


