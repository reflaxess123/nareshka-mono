from dataclasses import dataclass
from typing import Dict, List, Any, Optional


@dataclass
class CategoryStats:
    """Статистика по категории"""
    name: str
    total: int
    completed: int
    percentage: float
    subCategories: Dict[str, Any]


@dataclass
class ContentBlockStats:
    """Статистика по блоку контента"""
    id: str
    title: str
    solveCount: int
    isSolved: bool


@dataclass
class SubCategoryContentStats:
    """Статистика по подкатегории контента"""
    total: int
    solved: int
    percentage: float
    averageSolveCount: float
    blocks: List[ContentBlockStats]


@dataclass
class CategoryContentStats:
    """Статистика по категории контента"""
    total: int
    solved: int
    percentage: float
    averageSolveCount: float
    subCategories: Dict[str, SubCategoryContentStats]


@dataclass
class ContentStats:
    """Общая статистика по контенту"""
    categories: Dict[str, CategoryContentStats]
    totalBlocks: int
    solvedBlocks: int
    averageSolveCount: float


@dataclass
class TheoryCardStats:
    """Статистика по карточке теории"""
    id: str
    question: str
    reviewCount: int
    isReviewed: bool
    cardState: str
    easeFactor: float


@dataclass
class SubCategoryTheoryStats:
    """Статистика по подкатегории теории"""
    total: int
    reviewed: int
    percentage: float
    averageReviewCount: float
    cards: List[TheoryCardStats]


@dataclass
class CategoryTheoryStats:
    """Статистика по категории теории"""
    total: int
    reviewed: int
    percentage: float
    averageReviewCount: float
    subCategories: Dict[str, SubCategoryTheoryStats]


@dataclass
class TheoryStats:
    """Общая статистика по теории"""
    categories: Dict[str, CategoryTheoryStats]
    totalCards: int
    reviewedCards: int
    averageReviewCount: float


@dataclass
class OverallProgressStats:
    """Общий прогресс пользователя"""
    totalItems: int
    completedItems: int
    percentage: float
    contentPercentage: float
    theoryPercentage: float


@dataclass
class UserStatsOverview:
    """Общая статистика пользователя"""
    userId: int
    totalContentBlocks: int
    solvedContentBlocks: int
    totalTheoryCards: int
    reviewedTheoryCards: int
    contentProgress: Dict[str, Any]
    theoryProgress: Dict[str, Any]
    overallProgress: OverallProgressStats


@dataclass
class SubCategoryRoadmapStats:
    """Статистика подкатегории для roadmap"""
    name: str
    contentProgress: int
    theoryProgress: int
    overallProgress: int


@dataclass
class ItemStats:
    """Общая статистика по элементам"""
    total: int
    completed: int


@dataclass
class CategoryRoadmapStats:
    """Статистика категории для roadmap"""
    name: str
    contentProgress: int
    theoryProgress: int
    overallProgress: int
    contentStats: ItemStats
    theoryStats: ItemStats
    subCategories: List[SubCategoryRoadmapStats]


@dataclass
class RoadmapStats:
    """Roadmap статистика"""
    categories: List[CategoryRoadmapStats] 