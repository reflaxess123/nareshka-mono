"""Mindmap types для внутреннего использования в services и repositories."""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel


class TechnologyCenter(BaseModel):
    """Центральный узел технологии"""
    technology: str
    display_name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class Topic(BaseModel):
    """Топик в mind map"""
    key: str
    title: str
    description: Optional[str] = None
    technology: str
    position: Dict[str, float] = {}  # x, y coordinates
    difficulty: Optional[str] = None
    prerequisites: List[str] = []
    is_active: bool = True


class TaskDetail(BaseModel):
    """Детали задачи"""
    id: str
    title: str
    description: Optional[str] = None
    topic_key: str
    difficulty: Optional[str] = None
    is_completed: bool = False
    progress_percentage: float = 0.0
    attempt_count: int = 0
    last_attempt_at: Optional[str] = None


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


class MindMapResponse(BaseModel):
    """Ответ с данными mind map"""
    nodes: List[MindMapNode]
    edges: List[MindMapEdge]
    technology_center: Optional[TechnologyCenter] = None 