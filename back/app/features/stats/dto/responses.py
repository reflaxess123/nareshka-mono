"""DTO ответов для работы со статистикой"""

from typing import Any, Dict, List

from pydantic import BaseModel


class OverallProgressResponse(BaseModel):
    """Общий прогресс пользователя"""

    totalItems: int
    completedItems: int
    percentage: float
    contentPercentage: float
    theoryPercentage: float

    class Config:
        from_attributes = True


class UserStatsOverviewResponse(BaseModel):
    """Общая статистика пользователя"""

    userId: int
    totalContentBlocks: int
    solvedContentBlocks: int
    totalTheoryCards: int
    reviewedTheoryCards: int
    contentProgress: Dict[str, Any]
    theoryProgress: Dict[str, Any]
    overallProgress: Dict[str, Any]

    class Config:
        from_attributes = True


class ContentBlockStatsResponse(BaseModel):
    """Статистика контентного блока"""

    id: str
    title: str
    solveCount: int
    isSolved: bool

    class Config:
        from_attributes = True


class TheoryCardStatsResponse(BaseModel):
    """Статистика теоретической карточки"""

    id: str
    question: str
    reviewCount: int
    isReviewed: bool
    cardState: str
    easeFactor: float

    class Config:
        from_attributes = True


class SubCategoryContentStatsResponse(BaseModel):
    """Статистика подкатегории контента"""

    total: int
    solved: int
    percentage: float
    averageSolveCount: float
    blocks: List[ContentBlockStatsResponse]

    class Config:
        from_attributes = True


class SubCategoryTheoryStatsResponse(BaseModel):
    """Статистика подкатегории теории"""

    total: int
    reviewed: int
    percentage: float
    averageReviewCount: float
    cards: List[TheoryCardStatsResponse]

    class Config:
        from_attributes = True


class CategoryContentStatsResponse(BaseModel):
    """Статистика категории контента"""

    total: int
    solved: int
    percentage: float
    averageSolveCount: float
    subCategories: Dict[str, SubCategoryContentStatsResponse]

    class Config:
        from_attributes = True


class CategoryTheoryStatsResponse(BaseModel):
    """Статистика категории теории"""

    total: int
    reviewed: int
    percentage: float
    averageReviewCount: float
    subCategories: Dict[str, SubCategoryTheoryStatsResponse]

    class Config:
        from_attributes = True


class ContentStatsResponse(BaseModel):
    """Детальная статистика по контенту"""

    categories: Dict[str, Any]
    totalBlocks: int
    solvedBlocks: int
    averageSolveCount: float

    class Config:
        from_attributes = True


class TheoryStatsResponse(BaseModel):
    """Детальная статистика по теории"""

    categories: Dict[str, Any]
    totalCards: int
    reviewedCards: int
    averageReviewCount: float

    class Config:
        from_attributes = True


class ItemStatsResponse(BaseModel):
    """Статистика элементов"""

    total: int
    completed: int

    class Config:
        from_attributes = True


class SubCategoryRoadmapResponse(BaseModel):
    """Roadmap подкатегории"""

    name: str
    contentProgress: int
    theoryProgress: int
    overallProgress: int

    class Config:
        from_attributes = True


class CategoryRoadmapResponse(BaseModel):
    """Roadmap категории"""

    name: str
    contentProgress: int
    theoryProgress: int
    overallProgress: int
    contentStats: ItemStatsResponse
    theoryStats: ItemStatsResponse
    subCategories: List[SubCategoryRoadmapResponse]

    class Config:
        from_attributes = True


class RoadmapStatsResponse(BaseModel):
    """Roadmap статистика по категориям"""

    categories: List[Dict[str, Any]]

    class Config:
        from_attributes = True


class StatsHealthResponse(BaseModel):
    """Ответ health check для статистики"""

    status: str
    module: str

    class Config:
        from_attributes = True
