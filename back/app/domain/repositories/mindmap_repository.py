from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..entities.mindmap import (
    TechnologyCenter, Topic, TaskDetail, TopicStats, TopicWithTasks
)

class MindMapRepository(ABC):
    """Интерфейс репозитория для работы с mindmap"""
    
    @abstractmethod
    def get_technology_center(self, technology: str) -> Optional[TechnologyCenter]:
        """Получить центральный узел технологии"""
        pass
    
    @abstractmethod
    def get_technology_topics(self, technology: str) -> List[Topic]:
        """Получить все топики для технологии"""
        pass
    
    @abstractmethod
    def get_topic_config(self, topic_key: str, technology: str) -> Optional[Topic]:
        """Получить конфигурацию топика"""
        pass
    
    @abstractmethod
    def get_overall_progress(self, user_id: int, technology: str) -> Optional[Dict[str, Any]]:
        """Получить общий прогресс пользователя по технологии"""
        pass
    
    @abstractmethod
    def get_topic_progress(self, user_id: int, topic: Topic) -> Optional[Dict[str, Any]]:
        """Получить прогресс пользователя по теме"""
        pass
    
    @abstractmethod
    def get_topic_tasks(
        self, 
        topic: Topic, 
        user_id: Optional[int] = None,
        difficulty_filter: Optional[str] = None
    ) -> List[TaskDetail]:
        """Получить задачи по теме"""
        pass
    
    @abstractmethod
    def get_task_by_id(self, task_id: str, user_id: Optional[int] = None) -> Optional[TaskDetail]:
        """Получить задачу по ID"""
        pass
    
    @abstractmethod
    def get_topic_stats(self, topic: Topic, user_id: Optional[int] = None) -> Optional[TopicStats]:
        """Получить статистику по теме"""
        pass
    
    @abstractmethod
    def get_available_technologies(self) -> List[str]:
        """Получить список доступных технологий"""
        pass 