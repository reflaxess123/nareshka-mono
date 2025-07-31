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
            
            if filters.get("technology"):
                query = query.filter(InterviewRecord.technologies.contains([filters["technology"]]))
            
            if filters.get("difficulty"):
                query = query.filter(InterviewRecord.difficulty_level == filters["difficulty"])
            
            if filters.get("stage"):
                query = query.filter(InterviewRecord.stage_number == filters["stage"])
            
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

    def get_technologies_list(self) -> List[str]:
        """Получение списка всех технологий"""
        # Используем функцию unnest для извлечения элементов из массива
        technologies = (
            self.session.query(func.unnest(InterviewRecord.technologies).label('tech'))
            .distinct()
            .order_by('tech')
            .all()
        )
        return [tech[0] for tech in technologies if tech[0]]

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
        difficulties = [i.difficulty_level for i in interviews if i.difficulty_level]
        durations = [i.duration_minutes for i in interviews if i.duration_minutes]
        
        avg_difficulty = sum(difficulties) / len(difficulties) if difficulties else None
        avg_duration = sum(durations) / len(durations) if durations else None

        # Популярные технологии
        tech_count = {}
        for interview in interviews:
            for tech in interview.technologies:
                tech_count[tech] = tech_count.get(tech, 0) + 1

        popular_technologies = sorted(tech_count.items(), key=lambda x: x[1], reverse=True)[:5]

        # Распределение по этапам
        stages_count = {}
        for interview in interviews:
            stage = interview.stage_number or 0
            stages_count[stage] = stages_count.get(stage, 0) + 1

        return {
            "company_name": company_name,
            "total_interviews": total_interviews,
            "avg_difficulty": avg_difficulty,
            "avg_duration": avg_duration,
            "popular_technologies": [tech for tech, count in popular_technologies],
            "stages_distribution": stages_count
        }

    def get_analytics_overview(self) -> Dict[str, Any]:
        """Получение общей аналитики"""
        total_interviews = self.session.query(func.count(InterviewRecord.id)).scalar()
        total_companies = self.session.query(func.count(func.distinct(InterviewRecord.company_name))).scalar()

        # Топ компании
        top_companies = (
            self.session.query(
                InterviewRecord.company_name,
                func.count(InterviewRecord.id).label('count'),
                func.avg(InterviewRecord.difficulty_level).label('avg_diff')
            )
            .group_by(InterviewRecord.company_name)
            .order_by(desc('count'))
            .limit(5)
            .all()
        )

        top_companies_list = [
            {
                "company_name": company,
                "total_interviews": count,
                "avg_difficulty": float(avg_diff) if avg_diff else None,
                "avg_duration": None,
                "popular_technologies": [],
                "stages_distribution": {}
            }
            for company, count, avg_diff in top_companies
        ]

        # Популярные технологии
        tech_subquery = self.session.query(func.unnest(InterviewRecord.technologies).label('tech')).subquery()
        popular_technologies = (
            self.session.query(
                tech_subquery.c.tech,
                func.count(tech_subquery.c.tech).label('count')
            )
            .group_by(tech_subquery.c.tech)
            .order_by(desc('count'))
            .limit(10)
            .all()
        )

        popular_tech_list = [{"name": tech, "count": count} for tech, count in popular_technologies if tech]

        # Распределение по сложности
        difficulty_dist = (
            self.session.query(
                InterviewRecord.difficulty_level,
                func.count(InterviewRecord.id).label('count')
            )
            .filter(InterviewRecord.difficulty_level.isnot(None))
            .group_by(InterviewRecord.difficulty_level)
            .all()
        )

        difficulty_distribution = {str(level): count for level, count in difficulty_dist}

        return {
            "total_interviews": total_interviews,
            "total_companies": total_companies,
            "top_companies": top_companies_list,
            "popular_technologies": popular_tech_list,
            "difficulty_distribution": difficulty_distribution,
            "monthly_stats": []  # TODO: добавить месячную статистику
        }