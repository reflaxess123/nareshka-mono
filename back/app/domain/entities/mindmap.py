from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime

@dataclass
class TechnologyCenter:
    """Центральный узел технологии"""
    technology: str
    title: str
    description: str
    icon: str
    color: str
    main_category: str
    overall_progress: Optional[Dict[str, Any]] = None

@dataclass
class Topic:
    """Тема/топик mindmap"""
    key: str
    title: str
    description: str
    icon: str
    color: str
    main_category: str
    sub_category: str
    progress: Optional[Dict[str, Any]] = None

@dataclass
class MindMapNode:
    """Узел mindmap"""
    id: str
    type: str  # 'center' или 'topic'
    position: Dict[str, float]  # {'x': float, 'y': float}
    data: Dict[str, Any]

@dataclass
class MindMapEdge:
    """Связь между узлами mindmap"""
    id: str
    source: str
    target: str
    style: Dict[str, Any]
    animated: bool = True

@dataclass
class MindMapResponse:
    """Ответ с данными mindmap"""
    nodes: List[MindMapNode]
    edges: List[MindMapEdge]
    layout: str
    total_nodes: int
    total_edges: int
    structure_type: str
    active_topics: int
    applied_filters: Dict[str, Optional[str]]
    overall_progress: Optional[Dict[str, Any]] = None

@dataclass
class TaskDetail:
    """Детали задачи"""
    id: str
    title: str
    description: str
    has_code: bool
    code_content: Optional[str] = None
    code_language: Optional[str] = None
    progress: Optional[Dict[str, Any]] = None

@dataclass
class TopicStats:
    """Статистика по теме"""
    total_tasks: int
    completed_tasks: int
    completion_rate: float

@dataclass
class TopicWithTasks:
    """Тема с задачами"""
    topic: Topic
    tasks: List[TaskDetail]
    stats: Optional[TopicStats] = None 