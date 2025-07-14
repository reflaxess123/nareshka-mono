"""Response DTOs для mindmap feature"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class TechnologyConfigResponse(BaseModel):
    """Конфигурация технологии"""

    title: str
    description: str
    icon: str
    color: str


class ProgressResponse(BaseModel):
    """Прогресс пользователя"""

    totalTasks: int
    completedTasks: int
    completionRate: float
    status: Optional[str] = None


class MindMapNodeResponse(BaseModel):
    """Узел mindmap"""

    id: str
    type: str
    position: Dict[str, float]
    data: Dict[str, Any]


class MindMapEdgeResponse(BaseModel):
    """Связь mindmap"""

    id: str
    source: str
    target: str
    style: Dict[str, Any]
    animated: bool


class MindMapDataResponse(BaseModel):
    """Данные mindmap"""

    nodes: List[MindMapNodeResponse]
    edges: List[MindMapEdgeResponse]
    layout: str
    total_nodes: int
    total_edges: int
    structure_type: str
    active_topics: int
    applied_filters: Dict[str, Optional[str]]
    overall_progress: Optional[Dict[str, Any]] = None


class MindMapResponse(BaseModel):
    """Ответ с данными mindmap"""

    success: bool = True
    data: MindMapDataResponse
    structure_type: str
    metadata: Dict[str, Any]


class TechnologiesDataResponse(BaseModel):
    """Данные о технологиях"""

    technologies: List[str]
    configs: Dict[str, TechnologyConfigResponse]


class TechnologiesResponse(BaseModel):
    """Ответ с доступными технологиями"""

    success: bool = True
    data: TechnologiesDataResponse


class TopicResponse(BaseModel):
    """Информация о теме"""

    key: str
    title: str
    icon: str
    color: str
    description: str
    progress: Optional[Dict[str, Any]] = None


class TaskProgressResponse(BaseModel):
    """Прогресс по задаче"""

    solvedCount: int
    isCompleted: bool


class TaskResponse(BaseModel):
    """Задача"""

    id: str
    title: str
    description: str
    hasCode: bool
    progress: Optional[TaskProgressResponse] = None


class TopicStatsResponse(BaseModel):
    """Статистика по теме"""

    totalTasks: int
    completedTasks: int
    completionRate: float


class TopicTasksResponse(BaseModel):
    """Ответ с задачами по теме"""

    success: bool = True
    topic: TopicResponse
    tasks: List[TaskResponse]
    stats: Optional[TopicStatsResponse] = None


class TaskDetailResponse(BaseModel):
    """Детали задачи"""

    id: str
    title: str
    description: str
    hasCode: bool
    codeContent: Optional[str] = None
    codeLanguage: Optional[str] = None
    progress: Optional[TaskProgressResponse] = None


class TaskDetailResponseWrapper(BaseModel):
    """Обертка для деталей задачи"""

    success: bool = True
    task: TaskDetailResponse


class HealthResponse(BaseModel):
    """Ответ health check"""

    status: str
    module: str 


