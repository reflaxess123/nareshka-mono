"""
Categories Repository - репозиторий для работы с категориями вопросов интервью
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import text, and_, or_, func
from sqlalchemy.orm import Session

from app.features.interviews.exceptions.interview_exceptions import (
    CategoryNotFoundError,
    ClusterNotFoundError
)


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
            categories.append({
                'id': row.id,
                'name': row.name,
                'questions_count': row.questions_count,
                'clusters_count': row.clusters_count,
                'percentage': float(row.percentage),
                'color': row.color,
                'icon': row.icon
            })
        
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
            {'category_id': category_id}
        ).first()
        
        if not result:
            raise CategoryNotFoundError(f"Category {category_id} not found")
        
        return {
            'id': result.id,
            'name': result.name,
            'questions_count': result.questions_count,
            'clusters_count': result.clusters_count,
            'percentage': float(result.percentage),
            'color': result.color,
            'icon': result.icon
        }
    
    def get_clusters_by_category(
        self, 
        category_id: str,
        limit: Optional[int] = None
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
            text(query),
            {'category_id': category_id}
        ).fetchall()
        
        clusters = []
        for row in result:
            clusters.append({
                'id': row.id,
                'name': row.name,
                'category_id': row.category_id,
                'keywords': row.keywords[:5] if row.keywords else [],
                'questions_count': row.questions_count,
                'example_question': row.example_question
            })
        
        return clusters
    
    def get_questions_by_category(
        self,
        category_id: str,
        limit: int = 10,
        offset: int = 0,
        random: bool = False
    ) -> List[Dict[str, Any]]:
        """Получить вопросы категории"""
        order_clause = "ORDER BY RANDOM()" if random else "ORDER BY id"
        
        result = self.session.execute(
            text(f"""
                SELECT 
                    id, 
                    question_text, 
                    company, 
                    cluster_id, 
                    category_id, 
                    topic_name, 
                    canonical_question
                FROM "InterviewQuestion"
                WHERE category_id = :category_id
                {order_clause}
                LIMIT :limit OFFSET :offset
            """),
            {
                'category_id': category_id,
                'limit': limit,
                'offset': offset
            }
        ).fetchall()
        
        questions = []
        for row in result:
            questions.append({
                'id': row.id,
                'question_text': row.question_text,
                'company': row.company,
                'cluster_id': row.cluster_id,
                'category_id': row.category_id,
                'topic_name': row.topic_name,
                'canonical_question': row.canonical_question
            })
        
        return questions
    
    def get_questions_by_cluster(
        self,
        cluster_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Получить вопросы кластера"""
        result = self.session.execute(
            text("""
                SELECT 
                    id, 
                    question_text, 
                    company, 
                    cluster_id, 
                    category_id, 
                    topic_name, 
                    canonical_question
                FROM "InterviewQuestion"
                WHERE cluster_id = :cluster_id
                ORDER BY company, id
                LIMIT :limit OFFSET :offset
            """),
            {
                'cluster_id': cluster_id,
                'limit': limit,
                'offset': offset
            }
        ).fetchall()
        
        questions = []
        for row in result:
            questions.append({
                'id': row.id,
                'question_text': row.question_text,
                'company': row.company,
                'cluster_id': row.cluster_id,
                'category_id': row.category_id,
                'topic_name': row.topic_name,
                'canonical_question': row.canonical_question
            })
        
        return questions
    
    def search_questions(
        self,
        search_query: str,
        category_id: Optional[str] = None,
        company: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Поиск вопросов"""
        query = """
            SELECT 
                id, 
                question_text, 
                company, 
                cluster_id, 
                category_id, 
                topic_name, 
                canonical_question
            FROM "InterviewQuestion"
            WHERE LOWER(question_text) LIKE LOWER(:search_pattern)
        """
        
        params = {
            'search_pattern': f'%{search_query}%',
            'limit': limit
        }
        
        if category_id:
            query += " AND category_id = :category_id"
            params['category_id'] = category_id
        
        if company:
            query += " AND LOWER(company) = LOWER(:company)"
            params['company'] = company
        
        query += " LIMIT :limit"
        
        result = self.session.execute(text(query), params).fetchall()
        
        questions = []
        for row in result:
            questions.append({
                'id': row.id,
                'question_text': row.question_text,
                'company': row.company,
                'cluster_id': row.cluster_id,
                'category_id': row.category_id,
                'topic_name': row.topic_name,
                'canonical_question': row.canonical_question
            })
        
        return questions
    
    def get_category_statistics(self) -> Dict[str, Any]:
        """Получить общую статистику по категориям"""
        total_questions = self.session.execute(
            text("SELECT COUNT(*) FROM \"InterviewQuestion\"")
        ).scalar()
        
        categorized_questions = self.session.execute(
            text("SELECT COUNT(*) FROM \"InterviewQuestion\" WHERE category_id IS NOT NULL")
        ).scalar()
        
        total_categories = self.session.execute(
            text("SELECT COUNT(*) FROM \"InterviewCategory\"")
        ).scalar()
        
        total_clusters = self.session.execute(
            text("SELECT COUNT(*) FROM \"InterviewCluster\"")
        ).scalar()
        
        return {
            'total_questions': total_questions,
            'categorized_questions': categorized_questions,
            'total_categories': total_categories,
            'total_clusters': total_clusters,
            'categorization_rate': (categorized_questions / total_questions * 100) if total_questions > 0 else 0
        }