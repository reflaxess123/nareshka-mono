"""Stats types для внутреннего использования в services и repositories."""

from typing import Any, Dict, List

from pydantic import BaseModel


class UserStatsOverview(BaseModel):
    """Общая статистика пользователя"""

    total_content_blocks: int
    completed_content_blocks: int
    content_progress_percentage: float
    total_theory_cards: int
    completed_theory_cards: int
    theory_progress_percentage: float
    total_tasks_attempted: int
    total_tasks_solved: int
    task_success_rate: float
    learning_streak_days: int
    total_study_time_minutes: int


class ContentStats(BaseModel):
    """Детальная статистика по контенту"""

    total_blocks: int
    completed_blocks: int
    in_progress_blocks: int
    not_started_blocks: int
    progress_percentage: float
    blocks_by_category: Dict[str, Dict[str, Any]]
    recent_progress: List[Dict[str, Any]]
    difficulty_breakdown: Dict[str, int]


class TheoryStats(BaseModel):
    """Детальная статистика по теории"""

    total_cards: int
    completed_cards: int
    in_progress_cards: int
    not_started_cards: int
    progress_percentage: float
    cards_by_category: Dict[str, Dict[str, Any]]
    recent_progress: List[Dict[str, Any]]
    difficulty_breakdown: Dict[str, int]


class RoadmapStats(BaseModel):
    """Roadmap статистика по категориям"""

    categories: List[Dict[str, Any]]
    total_categories: int
    completed_categories: int
    in_progress_categories: int
    overall_progress_percentage: float
