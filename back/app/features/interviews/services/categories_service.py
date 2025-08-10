"""
Categories Service - сервис для работы с категориями вопросов
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.features.interviews.repositories.categories_repository import CategoriesRepository
from app.features.interviews.dto.categories_responses import (
    CategoryResponse,
    ClusterResponse,
    QuestionResponse,
    CategoryDetailResponse,
    CategoriesStatisticsResponse,
    CompanyResponse
)


class CategoriesService:
    """Сервис для работы с категориями вопросов"""
    
    def __init__(self, session: Session):
        self.repository = CategoriesRepository(session)
        self.session = session
    
    def get_all_categories(self) -> List[CategoryResponse]:
        """Получить все категории"""
        categories_data = self.repository.get_all_categories()
        
        return [
            CategoryResponse(
                id=cat['id'],
                name=cat['name'],
                questions_count=cat['questions_count'],
                clusters_count=cat['clusters_count'],
                percentage=cat['percentage'],
                color=cat.get('color'),
                icon=cat.get('icon')
            )
            for cat in categories_data
        ]
    
    def get_category_detail(
        self, 
        category_id: str,
        limit_questions: int = 10
    ) -> CategoryDetailResponse:
        """Получить детальную информацию о категории"""
        
        # Получаем категорию
        category_data = self.repository.get_category_by_id(category_id)
        category = CategoryResponse(
            id=category_data['id'],
            name=category_data['name'],
            questions_count=category_data['questions_count'],
            clusters_count=category_data['clusters_count'],
            percentage=category_data['percentage'],
            color=category_data.get('color'),
            icon=category_data.get('icon')
        )
        
        # Получаем кластеры
        clusters_data = self.repository.get_clusters_by_category(category_id)
        clusters = [
            ClusterResponse(
                id=cluster['id'],
                name=cluster['name'],
                category_id=cluster['category_id'],
                keywords=cluster['keywords'],
                questions_count=cluster['questions_count'],
                example_question=cluster.get('example_question')
            )
            for cluster in clusters_data
        ]
        
        # Получаем примеры вопросов
        questions_data = self.repository.get_questions_by_category(
            category_id=category_id,
            limit=limit_questions,
            random=True
        )
        sample_questions = [
            QuestionResponse(
                id=q['id'],
                question_text=q['question_text'],
                company=q.get('company'),
                cluster_id=q.get('cluster_id'),
                category_id=q.get('category_id'),
                topic_name=q.get('topic_name'),
                canonical_question=q.get('canonical_question')
            )
            for q in questions_data
        ]
        
        return CategoryDetailResponse(
            category=category,
            clusters=clusters,
            sample_questions=sample_questions
        )
    
    def get_cluster_questions(
        self,
        cluster_id: int,
        page: int = 1,
        limit: int = 50
    ) -> List[QuestionResponse]:
        """Получить вопросы кластера"""
        offset = (page - 1) * limit
        
        questions_data = self.repository.get_questions_by_cluster(
            cluster_id=cluster_id,
            limit=limit,
            offset=offset
        )
        
        return [
            QuestionResponse(
                id=q['id'],
                question_text=q['question_text'],
                company=q.get('company'),
                cluster_id=q.get('cluster_id'),
                category_id=q.get('category_id'),
                topic_name=q.get('topic_name'),
                canonical_question=q.get('canonical_question')
            )
            for q in questions_data
        ]
    
    def search_questions(
        self,
        search_query: str,
        category_id: Optional[str] = None,
        company: Optional[str] = None,
        limit: int = 50
    ) -> List[QuestionResponse]:
        """Поиск вопросов"""
        
        questions_data = self.repository.search_questions(
            search_query=search_query,
            category_id=category_id,
            company=company,
            limit=limit
        )
        
        return [
            QuestionResponse(
                id=q['id'],
                question_text=q['question_text'],
                company=q.get('company'),
                cluster_id=q.get('cluster_id'),
                category_id=q.get('category_id'),
                topic_name=q.get('topic_name'),
                canonical_question=q.get('canonical_question')
            )
            for q in questions_data
        ]
    
    def get_statistics(self) -> CategoriesStatisticsResponse:
        """Получить общую статистику"""
        stats = self.repository.get_category_statistics()
        
        return CategoriesStatisticsResponse(
            total_questions=stats['total_questions'],
            categorized_questions=stats['categorized_questions'],
            total_categories=stats['total_categories'],
            total_clusters=stats['total_clusters'],
            categorization_rate=stats['categorization_rate']
        )
    
    def get_top_companies(self, limit: int = 20) -> List[CompanyResponse]:
        """Получить топ компаний по количеству вопросов"""
        companies_data = self.repository.get_top_companies(limit=limit)
        
        return [
            CompanyResponse(
                name=company['name'],
                count=company['count']
            )
            for company in companies_data
        ]