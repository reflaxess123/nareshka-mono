"""Сервис для работы с интервью"""

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.features.interviews.dto.responses import (
    AnalyticsResponse,
    CompanyStatsResponse,
    InterviewDetailResponse,
    InterviewRecordResponse,
    InterviewsListResponse,
)
from app.features.interviews.repositories.interview_repository import (
    InterviewRepository,
)


class InterviewService:
    """Сервис для работы с интервью"""

    def __init__(self, session: Session):
        self.repository = InterviewRepository(session)

    def get_interviews_list(
        self, page: int = 1, limit: int = 20, filters: Optional[Dict[str, Any]] = None
    ) -> InterviewsListResponse:
        """Получение списка интервью с пагинацией"""
        interviews, total = self.repository.get_interviews(page, limit, filters)

        # Преобразование в DTO
        interview_responses = [
            InterviewRecordResponse.model_validate(interview)
            for interview in interviews
        ]

        has_next = page * limit < total
        has_prev = page > 1

        return InterviewsListResponse(
            interviews=interview_responses,
            total=total,
            page=page,
            limit=limit,
            has_next=has_next,
            has_prev=has_prev,
        )

    def get_interview_by_id(
        self, interview_id: str
    ) -> Optional[InterviewDetailResponse]:
        """Получение детальной информации об интервью"""
        interview = self.repository.get_interview_by_id(interview_id)

        if not interview:
            return None

        return InterviewDetailResponse.model_validate(interview)

    def get_companies_list(self) -> list[dict]:
        """Получение списка компаний"""
        return self.repository.get_companies_with_count()

    def get_companies_with_count(self) -> list[dict]:
        """Получение списка компаний с количеством вопросов"""
        return self.repository.get_companies_with_count()

    def get_company_statistics(
        self, company_name: str
    ) -> Optional[CompanyStatsResponse]:
        """Получение статистики по компании"""
        stats = self.repository.get_company_statistics(company_name)

        if not stats:
            return None

        return CompanyStatsResponse(**stats)

    def get_analytics_overview(self) -> AnalyticsResponse:
        """Получение общей аналитики"""
        analytics = self.repository.get_analytics_overview()
        return AnalyticsResponse(**analytics)
