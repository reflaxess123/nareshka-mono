from typing import Dict, List, Any
from pydantic import BaseModel


# Response DTOs для статистики
class OverallProgressDTO(BaseModel):
    totalItems: int
    completedItems: int
    percentage: float
    contentPercentage: float
    theoryPercentage: float


class UserStatsOverviewDTO(BaseModel):
    userId: int
    totalContentBlocks: int
    solvedContentBlocks: int
    totalTheoryCards: int
    reviewedTheoryCards: int
    contentProgress: Dict[str, Any]
    theoryProgress: Dict[str, Any]
    overallProgress: Dict[str, Any]


class ContentStatsDTO(BaseModel):
    categories: Dict[str, Any]
    totalBlocks: int
    solvedBlocks: int
    averageSolveCount: float


class TheoryStatsDTO(BaseModel):
    categories: Dict[str, Any]
    totalCards: int
    reviewedCards: int
    averageReviewCount: float


class RoadmapStatsDTO(BaseModel):
    categories: List[Dict[str, Any]]


# Вспомогательные DTOs для детализации
class ContentBlockDTO(BaseModel):
    id: str
    title: str
    solveCount: int
    isSolved: bool


class TheoryCardDTO(BaseModel):
    id: str
    question: str
    reviewCount: int
    isReviewed: bool
    cardState: str
    easeFactor: float


class SubCategoryContentDTO(BaseModel):
    total: int
    solved: int
    percentage: float
    averageSolveCount: float
    blocks: List[ContentBlockDTO]


class SubCategoryTheoryDTO(BaseModel):
    total: int
    reviewed: int
    percentage: float
    averageReviewCount: float
    cards: List[TheoryCardDTO]


class CategoryContentDTO(BaseModel):
    total: int
    solved: int
    percentage: float
    averageSolveCount: float
    subCategories: Dict[str, SubCategoryContentDTO]


class CategoryTheoryDTO(BaseModel):
    total: int
    reviewed: int
    percentage: float
    averageReviewCount: float
    subCategories: Dict[str, SubCategoryTheoryDTO]


class SubCategoryRoadmapDTO(BaseModel):
    name: str
    contentProgress: int
    theoryProgress: int
    overallProgress: int


class ItemStatsDTO(BaseModel):
    total: int
    completed: int


class CategoryRoadmapDTO(BaseModel):
    name: str
    contentProgress: int
    theoryProgress: int
    overallProgress: int
    contentStats: ItemStatsDTO
    theoryStats: ItemStatsDTO
    subCategories: List[SubCategoryRoadmapDTO] 