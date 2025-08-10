"""
Categories DTO Responses - модели ответов для категорий вопросов
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class CategoryResponse(BaseModel):
    """Модель ответа для категории"""
    id: str = Field(..., description="ID категории")
    name: str = Field(..., description="Название категории")
    questions_count: int = Field(..., description="Количество вопросов")
    clusters_count: int = Field(..., description="Количество кластеров")
    percentage: float = Field(..., description="Процент от общего числа вопросов")
    color: Optional[str] = Field(None, description="Цвет категории для UI")
    icon: Optional[str] = Field(None, description="Иконка категории")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "javascript_core",
                "name": "JavaScript Core",
                "questions_count": 2082,
                "clusters_count": 60,
                "percentage": 24.4,
                "color": "#f7df1e",
                "icon": "javascript"
            }
        }


class ClusterResponse(BaseModel):
    """Модель ответа для кластера"""
    id: int = Field(..., description="ID кластера")
    name: str = Field(..., description="Название кластера")
    category_id: str = Field(..., description="ID категории")
    keywords: List[str] = Field(..., description="Ключевые слова")
    questions_count: int = Field(..., description="Количество вопросов")
    example_question: Optional[str] = Field(None, description="Пример вопроса")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 25,
                "name": "Замыкания и область видимости",
                "category_id": "javascript_core",
                "keywords": ["closure", "scope", "замыкание", "область", "видимости"],
                "questions_count": 38,
                "example_question": "Что такое замыкание в JavaScript?"
            }
        }


class QuestionResponse(BaseModel):
    """Модель ответа для вопроса"""
    id: str = Field(..., description="ID вопроса")
    question_text: str = Field(..., description="Текст вопроса")
    company: Optional[str] = Field(None, description="Компания")
    cluster_id: Optional[int] = Field(None, description="ID кластера")
    category_id: Optional[str] = Field(None, description="ID категории")
    topic_name: Optional[str] = Field(None, description="Название топика")
    canonical_question: Optional[str] = Field(None, description="Канонический вопрос")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "q123",
                "question_text": "Объясните, что такое замыкание в JavaScript",
                "company": "Яндекс",
                "cluster_id": 25,
                "category_id": "javascript_core",
                "topic_name": "Замыкания и область видимости",
                "canonical_question": "Что такое замыкание?"
            }
        }


class CategoryDetailResponse(BaseModel):
    """Детальная информация о категории"""
    category: CategoryResponse = Field(..., description="Информация о категории")
    clusters: List[ClusterResponse] = Field(..., description="Кластеры категории")
    sample_questions: List[QuestionResponse] = Field(..., description="Примеры вопросов")
    
    class Config:
        json_schema_extra = {
            "example": {
                "category": {
                    "id": "javascript_core",
                    "name": "JavaScript Core",
                    "questions_count": 2082,
                    "clusters_count": 60,
                    "percentage": 24.4
                },
                "clusters": [
                    {
                        "id": 25,
                        "name": "Замыкания",
                        "category_id": "javascript_core",
                        "keywords": ["closure"],
                        "questions_count": 38
                    }
                ],
                "sample_questions": [
                    {
                        "id": "q123",
                        "question_text": "Что такое замыкание?",
                        "company": "Яндекс"
                    }
                ]
            }
        }


class CategoriesStatisticsResponse(BaseModel):
    """Статистика по категориям"""
    total_questions: int = Field(..., description="Всего вопросов")
    categorized_questions: int = Field(..., description="Категоризировано вопросов")
    total_categories: int = Field(..., description="Всего категорий")
    total_clusters: int = Field(..., description="Всего кластеров")
    categorization_rate: float = Field(..., description="Процент категоризации")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_questions": 8532,
                "categorized_questions": 6649,
                "total_categories": 13,
                "total_clusters": 182,
                "categorization_rate": 77.9
            }
        }


class QuestionsListResponse(BaseModel):
    """Список вопросов с пагинацией"""
    questions: List[QuestionResponse] = Field(..., description="Список вопросов")
    total: int = Field(..., description="Общее количество вопросов")
    page: int = Field(..., description="Текущая страница")
    limit: int = Field(..., description="Количество на странице")
    has_next: bool = Field(..., description="Есть ли следующая страница")
    
    class Config:
        json_schema_extra = {
            "example": {
                "questions": [],
                "total": 100,
                "page": 1,
                "limit": 50,
                "has_next": True
            }
        }