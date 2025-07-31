"""Repository для работы с интервью"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_

from app.shared.entities.interview import InterviewRecord, InterviewAnalytics


class InterviewRepository:
    """Репозиторий для работы с интервью"""

    def __init__(self, session: Session):
        self.session = session

    def get_interviews(
        self,
        page: int = 1,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[InterviewRecord], int]:
        """Получение списка интервью с фильтрацией и пагинацией"""
        query = self.session.query(InterviewRecord)

        # Применение фильтров
        if filters:
            if filters.get("company"):
                query = query.filter(InterviewRecord.company_name.ilike(f"%{filters['company']}%"))
            
            
            if filters.get("search"):
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        InterviewRecord.content.ilike(search_term),
                        InterviewRecord.full_content.ilike(search_term),
                        InterviewRecord.company_name.ilike(search_term)
                    )
                )

        # Подсчет общего количества
        total = query.count()

        # Пагинация и сортировка
        interviews = (
            query
            .order_by(desc(InterviewRecord.interview_date))
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        return interviews, total

    def get_interview_by_id(self, interview_id: str) -> Optional[InterviewRecord]:
        """Получение интервью по ID"""
        return self.session.query(InterviewRecord).filter_by(id=interview_id).first()

    def get_companies_list(self) -> List[str]:
        """Получение списка всех компаний"""
        companies = (
            self.session.query(InterviewRecord.company_name)
            .distinct()
            .order_by(InterviewRecord.company_name)
            .all()
        )
        return [company[0] for company in companies]


    def get_company_statistics(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Получение статистики по компании"""
        interviews = (
            self.session.query(InterviewRecord)
            .filter(InterviewRecord.company_name == company_name)
            .all()
        )

        if not interviews:
            return None

        # Подсчет статистики
        total_interviews = len(interviews)
        durations = [i.duration_minutes for i in interviews if i.duration_minutes]
        
        avg_duration = sum(durations) / len(durations) if durations else None

        return {
            "company_name": company_name,
            "total_interviews": total_interviews,
            "avg_duration": avg_duration
        }

    def get_analytics_overview(self) -> Dict[str, Any]:
        """Получение общей аналитики"""
        total_interviews = self.session.query(func.count(InterviewRecord.id)).scalar()
        total_companies = self.session.query(func.count(func.distinct(InterviewRecord.company_name))).scalar()

        # Топ компании
        top_companies = (
            self.session.query(
                InterviewRecord.company_name,
                func.count(InterviewRecord.id).label('count')
            )
            .group_by(InterviewRecord.company_name)
            .order_by(desc('count'))
            .limit(5)
            .all()
        )

        top_companies_list = [
            {
                "company_name": company,
                "total_interviews": count
            }
            for company, count in top_companies
        ]

        return {
            "total_interviews": total_interviews,
            "total_companies": total_companies,
            "top_companies": top_companies_list,
            "monthly_stats": []  # TODO: добавить месячную статистику
        }