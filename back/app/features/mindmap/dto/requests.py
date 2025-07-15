"""Request DTOs для mindmap feature"""

from typing import Optional
from pydantic import BaseModel, Field


class MindMapGenerateRequest(BaseModel):
    """Запрос на генерацию mindmap"""

    structure_type: str = Field(default="topics", description="Тип структуры mindmap")
    technology: str = Field(default="javascript", description="Технология")
    difficulty_filter: Optional[str] = Field(
        default=None, description="Фильтр по сложности"
    )
    topic_filter: Optional[str] = Field(default=None, description="Фильтр по теме")


class TopicTasksRequest(BaseModel):
    """Запрос на получение задач по теме"""

    technology: str = Field(default="javascript", description="Технология")
    difficulty_filter: Optional[str] = Field(
        default=None, description="Фильтр по сложности"
    ) 


