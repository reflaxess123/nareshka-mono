"""Response DTO для interviews API"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class InterviewRecordResponse(BaseModel):
    """Ответ с данными интервью"""
    id: str
    company_name: str
    interview_date: datetime
    position: Optional[str]
    full_content: str
    tags: List[str]

    class Config:
        from_attributes = True


class InterviewDetailResponse(BaseModel):
    """Детальный ответ с полным контентом"""
    id: str
    company_name: str
    interview_date: datetime
    position: Optional[str]
    full_content: str  # Полная версия
    tags: List[str]
    companies: List[str]
    extracted_urls: List[str]

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
    avg_duration: Optional[int]


class CompaniesListResponse(BaseModel):
    """Список компаний"""
    companies: List[str]




class AnalyticsResponse(BaseModel):
    """Общая аналитика"""
    total_interviews: int
    total_companies: int
    top_companies: List[CompanyStatsResponse]
    monthly_stats: List[dict]