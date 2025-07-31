"""Response DTO для interviews API"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class InterviewRecordResponse(BaseModel):
    """Ответ с данными интервью"""
    id: str
    company_name: str
    interview_date: datetime
    stage_number: Optional[int]
    position: Optional[str]
    content: str
    duration_minutes: Optional[int]
    questions_count: Optional[int]
    technologies: List[str]
    difficulty_level: Optional[int]
    telegram_author: Optional[str]
    tags: List[str]
    createdAt: datetime

    class Config:
        from_attributes = True


class InterviewDetailResponse(BaseModel):
    """Детальный ответ с полным контентом"""
    id: str
    company_name: str
    interview_date: datetime
    stage_number: Optional[int]
    position: Optional[str]
    content: str
    full_content: str  # Полная версия
    duration_minutes: Optional[int]
    questions_count: Optional[int]
    technologies: List[str]
    difficulty_level: Optional[int]
    telegram_author: Optional[str]
    tags: List[str]
    companies: List[str]
    extracted_urls: List[str]
    createdAt: datetime

    class Config:
        from_attributes = True


class InterviewsListResponse(BaseModel):
    """Список интервью с пагинацией"""
    interviews: List[InterviewRecordResponse]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool


class CompanyStatsResponse(BaseModel):
    """Статистика по компании"""
    company_name: str
    total_interviews: int
    avg_difficulty: Optional[float]
    avg_duration: Optional[int]
    popular_technologies: List[str]
    stages_distribution: dict


class CompaniesListResponse(BaseModel):
    """Список компаний"""
    companies: List[str]


class TechnologiesListResponse(BaseModel):
    """Список технологий"""
    technologies: List[str]


class AnalyticsResponse(BaseModel):
    """Общая аналитика"""
    total_interviews: int
    total_companies: int
    top_companies: List[CompanyStatsResponse]
    popular_technologies: List[dict]
    difficulty_distribution: dict
    monthly_stats: List[dict]