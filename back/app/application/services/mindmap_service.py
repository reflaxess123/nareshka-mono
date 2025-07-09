import math
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...domain.repositories.mindmap_repository import MindMapRepository
from ...domain.entities.mindmap_types import (
    TechnologyCenter, Topic, TaskDetail, TopicStats, TopicWithTasks,
    MindMapNode, MindMapEdge, MindMapResponse
)

class MindMapService:
    """Сервис для работы с mindmap"""
    
    def __init__(self, mindmap_repository: MindMapRepository):
        self.mindmap_repository = mindmap_repository
    
    def generate_mindmap(
        self,
        user_id: Optional[int] = None,
        technology: str = "javascript",
        difficulty_filter: Optional[str] = None,
        topic_filter: Optional[str] = None
    ) -> MindMapResponse:
        """Генерация данных для mindmap"""
        # Получаем центральный узел технологии
        tech_center = self.mindmap_repository.get_technology_center(technology)
        if not tech_center:
            raise ValueError(f"Неподдерживаемая технология: {technology}")
        
        # Получаем общий прогресс пользователя если авторизован
        if user_id:
            overall_progress = self.mindmap_repository.get_overall_progress(user_id, technology)
            tech_center.overall_progress = overall_progress
        
        # Получаем топики для технологии
        all_topics = self.mindmap_repository.get_technology_topics(technology)
        
        # Применяем фильтры
        active_topics = all_topics
        if topic_filter:
            active_topics = [topic for topic in all_topics if topic.key == topic_filter]
        
        # Создаем узлы и связи
        nodes = []
        edges = []
        
        # Центральный узел
        center_node = MindMapNode(
            id="center",
            type="center",
            position={"x": 500, "y": 400},
            data={
                "title": tech_center.display_name,
                "description": tech_center.description,
                "icon": tech_center.icon,
                "color": tech_center.color,
                "type": "center",
                "technology": technology,
                "overallProgress": tech_center.overall_progress
            }
        )
        nodes.append(center_node)
        
        # Топики как узлы в радиальной структуре
        radius = 400
        topic_count = len(active_topics)
        
        for i, topic in enumerate(active_topics):
            angle = (2 * math.pi * i) / topic_count
            x = 500 + radius * math.cos(angle)
            y = 400 + radius * math.sin(angle)
            
            # Получаем прогресс по теме если пользователь авторизован
            if user_id:
                progress = self.mindmap_repository.get_topic_progress(user_id, topic)
                topic.progress = progress
            
            # Создаем узел топика
            topic_node = MindMapNode(
                id=f"topic_{topic.key}",
                type="topic",
                position={"x": x, "y": y},
                data={
                    "title": topic.title,
                    "icon": topic.icon,
                    "color": topic.color,
                    "description": topic.description,
                    "topic_key": topic.key,
                    "type": "topic",
                    "progress": topic.progress
                }
            )
            nodes.append(topic_node)
            
            # Создаем связь с центральным узлом
            edge = MindMapEdge(
                id=f"edge_center_{topic.key}",
                source="center",
                target=f"topic_{topic.key}",
                style={
                    "stroke": topic.color,
                    "strokeWidth": 3,
                    "strokeOpacity": 0.7
                },
                animated=True
            )
            edges.append(edge)
        
        return MindMapResponse(
            nodes=nodes,
            edges=edges,
            layout="radial",
            total_nodes=len(nodes),
            total_edges=len(edges),
            structure_type="topics_simple",
            active_topics=len(active_topics),
            applied_filters={
                "difficulty": difficulty_filter,
                "topic": topic_filter
            },
            overall_progress=tech_center.overall_progress
        )
    
    def get_available_technologies(self) -> Dict[str, Any]:
        """Получить доступные технологии с конфигурацией"""
        technologies = self.mindmap_repository.get_available_technologies()
        technology_configs = {}
        
        for tech in technologies:
            tech_center = self.mindmap_repository.get_technology_center(tech)
            if tech_center:
                technology_configs[tech] = {
                    "title": tech_center.display_name,
                    "description": tech_center.description,
                    "icon": tech_center.icon,
                    "color": tech_center.color
                }
        
        return {
            "technologies": technologies,
            "configs": technology_configs
        }
    
    def get_topic_with_tasks(
        self,
        topic_key: str,
        user_id: Optional[int] = None,
        technology: str = "javascript",
        difficulty_filter: Optional[str] = None
    ) -> TopicWithTasks:
        """Получить тему с задачами"""
        # Получаем конфигурацию топика
        topic = self.mindmap_repository.get_topic_config(topic_key, technology)
        if not topic:
            raise ValueError(f"Topic '{topic_key}' not found for technology '{technology}'")
        
        # Получаем задачи по теме
        tasks = self.mindmap_repository.get_topic_tasks(topic, user_id, difficulty_filter)
        
        # Получаем статистику по теме
        stats = None
        if user_id:
            stats = self.mindmap_repository.get_topic_stats(topic, user_id)
        
        return TopicWithTasks(
            topic=topic,
            tasks=tasks,
            stats=stats
        )
    
    def get_task_detail(self, task_id: str, user_id: Optional[int] = None) -> TaskDetail:
        """Получить детали задачи"""
        task = self.mindmap_repository.get_task_by_id(task_id, user_id)
        if not task:
            raise ValueError(f"Task with id '{task_id}' not found")
        
        return task
    
    def get_health_status(self) -> Dict[str, str]:
        """Получить статус здоровья модуля"""
        return {
            "status": "healthy",
            "module": "mindmap"
        } 