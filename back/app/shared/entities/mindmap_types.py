"""Mindmap types для внутреннего использования в services и repositories."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class TechnologyCenter(BaseModel):
    """Центральный узел технологии"""

    technology: str
    display_name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    main_category: Optional[str] = None
    overall_progress: Optional[Dict[str, Any]] = None


class Topic(BaseModel):
    """Топик в mind map"""

    key: str
    title: str
    description: Optional[str] = None
    technology: str = ""
    position: Dict[str, float] = {}  # x, y coordinates
    difficulty: Optional[str] = None
    prerequisites: List[str] = []
    is_active: bool = True
    icon: Optional[str] = None
    color: Optional[str] = None
    main_category: str
    sub_category: str
    progress: Optional[Dict[str, Any]] = None


class TaskDetail(BaseModel):
    """Детали задачи"""

    id: str
    title: str
    description: Optional[str] = None
    topic_key: str = ""
    difficulty: Optional[str] = None
    is_completed: bool = False
    progress_percentage: float = 0.0
    attempt_count: int = 0
    last_attempt_at: Optional[str] = None
    has_code: bool = False
    code_content: Optional[str] = None
    code_language: Optional[str] = None
    progress: Optional[Dict[str, Any]] = None


class TopicStats(BaseModel):
    """Статистика по топику"""

    topic_key: str
    total_tasks: int
    completed_tasks: int
    progress_percentage: float
    average_difficulty: Optional[str] = None
    last_activity_at: Optional[str] = None


class TopicWithTasks(BaseModel):
    """Топик с задачами"""

    topic: Topic
    tasks: List[TaskDetail]
    stats: Optional[TopicStats] = None


class MindMapNode(BaseModel):
    """Узел mind map"""

    id: str
    type: str
    data: Dict[str, Any]
    position: Dict[str, float] = {}


class MindMapEdge(BaseModel):
    """Связь в mind map"""

    id: str
    source: str
    target: str
    type: Optional[str] = None
    data: Dict[str, Any] = {}
    style: Dict[str, Any] = {}
    animated: bool = False


class MindMapResponse(BaseModel):
    """Ответ с данными mind map"""

    nodes: List[MindMapNode]
    edges: List[MindMapEdge]
    technology_center: Optional[TechnologyCenter] = None
    layout: str = "radial"
    total_nodes: int = 0
    total_edges: int = 0
    structure_type: str = "topics"
    active_topics: int = 0
    applied_filters: Dict[str, Any] = {}
    overall_progress: Optional[Dict[str, Any]] = None
