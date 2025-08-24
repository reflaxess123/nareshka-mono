"""
Categories Repository - репозиторий для работы с категориями вопросов интервью
"""

from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.features.interviews.exceptions.interview_exceptions import (
    CategoryNotFoundError,
)


class QuestionQueryBuilder:
    """Конструктор запросов для таблицы InterviewQuestion с переиспользуемой фильтрацией"""

    BASE_SELECT = """
        SELECT 
            id, 
            question_text, 
            company, 
            cluster_id, 
            category_id, 
            topic_name, 
            canonical_question,
            interview_id
        FROM "InterviewQuestion"
    """
    
    BASE_COUNT = 'SELECT COUNT(*) as count FROM "InterviewQuestion"'

    @classmethod
    def build_conditions_and_params(
        cls,
        search_query: Optional[str] = None,
        category_ids: Optional[List[str]] = None,
        cluster_ids: Optional[List[int]] = None,
        companies: Optional[List[str]] = None,
    ) -> tuple[List[str], Dict[str, Any]]:
        """Создает WHERE условия и параметры для запросов"""
        conditions = []
        params = {}

        # Обработка поискового запроса
        if search_query and search_query != "*":
            if search_query.startswith("interview:"):
                interview_id = search_query.replace("interview:", "")
                conditions.append("interview_id = :interview_id")
                params["interview_id"] = interview_id
            else:
                conditions.append("LOWER(question_text) LIKE LOWER(:search_pattern)")
                params["search_pattern"] = f"%{search_query}%"

        # Множественные категории
        if category_ids and len(category_ids) > 0:
            placeholders = ",".join([f":category_{i}" for i in range(len(category_ids))])
            conditions.append(f"category_id IN ({placeholders})")
            for i, category_id in enumerate(category_ids):
                params[f"category_{i}"] = category_id

        # Множественные кластеры
        if cluster_ids and len(cluster_ids) > 0:
            placeholders = ",".join([f":cluster_{i}" for i in range(len(cluster_ids))])
            conditions.append(f"cluster_id IN ({placeholders})")
            for i, cluster_id in enumerate(cluster_ids):
                params[f"cluster_{i}"] = cluster_id

        # Множественные компании
        if companies and len(companies) > 0:
            placeholders = ",".join([f":company_{i}" for i in range(len(companies))])
            conditions.append(f"LOWER(company) IN ({placeholders})")
            for i, company in enumerate(companies):
                params[f"company_{i}"] = company.lower()

        return conditions, params

    @classmethod
    def row_to_dict(cls, row) -> Dict[str, Any]:
        """Унифицированное преобразование row → dict для InterviewQuestion"""
        return {
            "id": row.id,
            "question_text": row.question_text,
            "company": row.company,
            "cluster_id": row.cluster_id,
            "category_id": row.category_id,
            "topic_name": row.topic_name,
            "canonical_question": row.canonical_question,
            "interview_id": row.interview_id,
        }


class CategoriesRepository:
    """Репозиторий для работы с категориями и кластерами вопросов"""

    def __init__(self, session: Session):
        self.session = session

    def get_all_categories(self) -> List[Dict[str, Any]]:
        """Получить все категории"""
        result = self.session.execute(
            text("""
                SELECT 
                    id, 
                    name, 
                    questions_count, 
                    clusters_count, 
                    percentage,
                    color,
                    icon
                FROM "InterviewCategory"
                ORDER BY questions_count DESC
            """)
        ).fetchall()

        categories = []
        for row in result:
            categories.append(
                {
                    "id": row.id,
                    "name": row.name,
                    "questions_count": row.questions_count,
                    "clusters_count": row.clusters_count,
                    "percentage": float(row.percentage),
                    "color": row.color,
                    "icon": row.icon,
                }
            )

        return categories

    def get_category_by_id(self, category_id: str) -> Optional[Dict[str, Any]]:
        """Получить категорию по ID"""
        result = self.session.execute(
            text("""
                SELECT 
                    id, 
                    name, 
                    questions_count, 
                    clusters_count, 
                    percentage,
                    color,
                    icon
                FROM "InterviewCategory"
                WHERE id = :category_id
            """),
            {"category_id": category_id},
        ).first()

        if not result:
            raise CategoryNotFoundError(f"Category {category_id} not found")

        return {
            "id": result.id,
            "name": result.name,
            "questions_count": result.questions_count,
            "clusters_count": result.clusters_count,
            "percentage": float(result.percentage),
            "color": result.color,
            "icon": result.icon,
        }

    def get_clusters_by_category(
        self, category_id: str, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Получить кластеры категории"""
        query = """
            SELECT 
                id, 
                name, 
                category_id, 
                keywords, 
                questions_count, 
                example_question
            FROM "InterviewCluster"
            WHERE category_id = :category_id
            ORDER BY questions_count DESC
        """

        if limit:
            query += f" LIMIT {limit}"

        result = self.session.execute(
            text(query), {"category_id": category_id}
        ).fetchall()

        clusters = []
        for row in result:
            clusters.append(
                {
                    "id": row.id,
                    "name": row.name,
                    "category_id": row.category_id,
                    "keywords": row.keywords[:5] if row.keywords else [],
                    "questions_count": row.questions_count,
                    "example_question": row.example_question,
                }
            )

        return clusters

    def get_questions_by_category(
        self, category_id: str, limit: int = 10, offset: int = 0, random: bool = False
    ) -> List[Dict[str, Any]]:
        """Получить вопросы категории"""
        order_clause = "ORDER BY RANDOM()" if random else "ORDER BY id"

        query = f"{QuestionQueryBuilder.BASE_SELECT} WHERE category_id = :category_id {order_clause} LIMIT :limit OFFSET :offset"

        result = self.session.execute(
            text(query),
            {"category_id": category_id, "limit": limit, "offset": offset},
        ).fetchall()

        return [QuestionQueryBuilder.row_to_dict(row) for row in result]

    def get_questions_by_cluster(
        self, cluster_id: int, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Получить вопросы кластера"""
        query = f"{QuestionQueryBuilder.BASE_SELECT} WHERE cluster_id = :cluster_id ORDER BY company, id LIMIT :limit OFFSET :offset"

        result = self.session.execute(
            text(query),
            {"cluster_id": cluster_id, "limit": limit, "offset": offset},
        ).fetchall()

        return [QuestionQueryBuilder.row_to_dict(row) for row in result]

    def search_questions(
        self,
        search_query: str,
        category_ids: Optional[List[str]] = None,
        cluster_ids: Optional[List[int]] = None,
        companies: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Поиск вопросов"""
        conditions, params = QuestionQueryBuilder.build_conditions_and_params(
            search_query=search_query,
            category_ids=category_ids,
            cluster_ids=cluster_ids,
            companies=companies,
        )

        query = QuestionQueryBuilder.BASE_SELECT
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY id LIMIT :limit OFFSET :offset"

        params.update({"limit": limit, "offset": offset})

        result = self.session.execute(text(query), params).fetchall()
        return [QuestionQueryBuilder.row_to_dict(row) for row in result]

    def count_questions(
        self,
        search_query: str,
        category_ids: Optional[List[str]] = None,
        cluster_ids: Optional[List[int]] = None,
        companies: Optional[List[str]] = None,
    ) -> int:
        """Подсчет количества вопросов для поиска"""
        conditions, params = QuestionQueryBuilder.build_conditions_and_params(
            search_query=search_query,
            category_ids=category_ids,
            cluster_ids=cluster_ids,
            companies=companies,
        )

        query = QuestionQueryBuilder.BASE_COUNT
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        result = self.session.execute(text(query), params).fetchone()
        return result.count

    def get_category_statistics(self) -> Dict[str, Any]:
        """Получить общую статистику по категориям"""
        total_questions = self.session.execute(
            text('SELECT COUNT(*) FROM "InterviewQuestion"')
        ).scalar()

        categorized_questions = self.session.execute(
            text(
                'SELECT COUNT(*) FROM "InterviewQuestion" WHERE category_id IS NOT NULL'
            )
        ).scalar()

        total_categories = self.session.execute(
            text('SELECT COUNT(*) FROM "InterviewCategory"')
        ).scalar()

        total_clusters = self.session.execute(
            text('SELECT COUNT(*) FROM "InterviewCluster"')
        ).scalar()

        return {
            "total_questions": total_questions,
            "categorized_questions": categorized_questions,
            "total_categories": total_categories,
            "total_clusters": total_clusters,
            "categorization_rate": (categorized_questions / total_questions * 100)
            if total_questions > 0
            else 0,
        }

    def get_top_companies(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Получить топ компаний по количеству вопросов"""
        result = self.session.execute(
            text("""
                SELECT 
                    company as name, 
                    COUNT(*) as count
                FROM "InterviewQuestion" 
                WHERE company IS NOT NULL 
                GROUP BY company 
                ORDER BY count DESC 
                LIMIT :limit
            """),
            {"limit": limit},
        )

        return [dict(row._mapping) for row in result]

    def count_total_companies(self) -> int:
        """Получить общее количество компаний"""
        result = self.session.execute(
            text("""
                SELECT COUNT(DISTINCT company) as count
                FROM "InterviewQuestion" 
                WHERE company IS NOT NULL AND company != ''
            """)
        ).scalar()

        return result or 0

    def get_all_clusters(
        self,
        category_id: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Получить все кластеры с фильтрацией"""
        query = """
            SELECT 
                id, 
                name, 
                category_id, 
                keywords, 
                questions_count, 
                example_question
            FROM "InterviewCluster"
        """

        conditions = []
        params = {"limit": limit}

        if category_id:
            conditions.append("category_id = :category_id")
            params["category_id"] = category_id

        if search and len(search.strip()) >= 2:
            conditions.append("LOWER(name) LIKE LOWER(:search)")
            params["search"] = f"%{search.strip()}%"

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY questions_count DESC, name ASC LIMIT :limit"

        result = self.session.execute(text(query), params).fetchall()

        clusters = []
        for row in result:
            clusters.append(
                {
                    "id": row.id,
                    "name": row.name,
                    "category_id": row.category_id,
                    "keywords": row.keywords[:5]
                    if row.keywords
                    else [],  # Ограничиваем количество ключевых слов
                    "questions_count": row.questions_count,
                    "example_question": row.example_question,
                }
            )

        return clusters
