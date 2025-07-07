from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, asc

from ...domain.repositories.mindmap_repository import MindMapRepository
from ...domain.entities.mindmap import (
    TechnologyCenter, Topic, TaskDetail, TopicStats, TopicWithTasks
)
from ..models import ContentBlock, ContentFile, UserContentProgress
from ...mindmap_config import (
    TECHNOLOGY_CENTERS, TECHNOLOGY_TOPICS, 
    get_technology_center, get_technology_topics,
    get_topic_config, get_available_technologies
)

class SqlAlchemyMindMapRepository(MindMapRepository):
    """SQLAlchemy реализация репозитория для mindmap"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_technology_center(self, technology: str) -> Optional[TechnologyCenter]:
        """Получить центральный узел технологии"""
        config = get_technology_center(technology)
        if not config:
            return None
        
        return TechnologyCenter(
            technology=technology,
            title=config['title'],
            description=config['description'],
            icon=config['icon'],
            color=config['color'],
            main_category=config['mainCategory']
        )
    
    def get_technology_topics(self, technology: str) -> List[Topic]:
        """Получить все топики для технологии"""
        topics_config = get_technology_topics(technology)
        topics = []
        
        for key, config in topics_config.items():
            topic = Topic(
                key=key,
                title=config['title'],
                description=config['description'],
                icon=config['icon'],
                color=config['color'],
                main_category=config['mainCategory'],
                sub_category=config['subCategory']
            )
            topics.append(topic)
        
        return topics
    
    def get_topic_config(self, topic_key: str, technology: str) -> Optional[Topic]:
        """Получить конфигурацию топика"""
        config = get_topic_config(topic_key, technology)
        if not config:
            return None
        
        return Topic(
            key=topic_key,
            title=config['title'],
            description=config['description'],
            icon=config['icon'],
            color=config['color'],
            main_category=config['mainCategory'],
            sub_category=config['subCategory']
        )
    
    def get_overall_progress(self, user_id: int, technology: str) -> Optional[Dict[str, Any]]:
        """Получить общий прогресс пользователя по технологии"""
        tech_center = self.get_technology_center(technology)
        if not tech_center:
            return None
        
        # Получаем общее количество задач с кодом для данной технологии
        total_tasks = self.session.query(func.count(ContentBlock.id)).join(ContentFile).filter(
            ContentBlock.codeContent.isnot(None),
            ContentFile.mainCategory == tech_center.main_category
        ).scalar() or 0
        
        # Получаем количество решенных задач
        completed_tasks = self.session.query(func.count(UserContentProgress.id)).filter(
            UserContentProgress.userId == user_id,
            UserContentProgress.solvedCount > 0
        ).join(ContentBlock).join(ContentFile).filter(
            ContentBlock.codeContent.isnot(None),
            ContentFile.mainCategory == tech_center.main_category
        ).scalar() or 0
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            "totalTasks": total_tasks,
            "completedTasks": completed_tasks,
            "completionRate": float(completion_rate)
        }
    
    def get_topic_progress(self, user_id: int, topic: Topic) -> Optional[Dict[str, Any]]:
        """Получить прогресс пользователя по теме"""
        # Общее количество задач в категории
        total_tasks = self.session.query(func.count(ContentBlock.id)).join(ContentFile).filter(
            ContentFile.mainCategory == topic.main_category,
            ContentFile.subCategory == topic.sub_category
        ).scalar() or 0
        
        # Количество решенных задач
        completed_tasks = self.session.query(func.count(UserContentProgress.id)).filter(
            UserContentProgress.userId == user_id,
            UserContentProgress.solvedCount > 0
        ).join(ContentBlock).join(ContentFile).filter(
            ContentFile.mainCategory == topic.main_category,
            ContentFile.subCategory == topic.sub_category
        ).scalar() or 0
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Определяем статус
        status = "not_started"
        if completed_tasks > 0:
            if completion_rate >= 100:
                status = "completed"
            else:
                status = "in_progress"
        
        return {
            "totalTasks": total_tasks,
            "completedTasks": completed_tasks,
            "completionRate": float(completion_rate),
            "status": status
        }
    
    def get_topic_tasks(
        self, 
        topic: Topic, 
        user_id: Optional[int] = None,
        difficulty_filter: Optional[str] = None
    ) -> List[TaskDetail]:
        """Получить задачи по теме"""
        query = self.session.query(ContentBlock).join(ContentFile)
        
        query = query.filter(
            func.lower(ContentFile.mainCategory) == func.lower(topic.main_category),
            func.lower(ContentFile.subCategory) == func.lower(topic.sub_category)
        )
        
        query = query.order_by(asc(ContentBlock.orderInFile))
        
        content_blocks = query.all()
        
        tasks = []
        for block in content_blocks:
            description = block.textContent or ""
            if description:
                description = description.replace("\\n", "\n").replace("\\t", "\t")
            
            # Получаем прогресс по задаче если пользователь авторизован
            progress = None
            if user_id:
                user_progress = self.session.query(UserContentProgress).filter(
                    and_(
                        UserContentProgress.userId == user_id,
                        UserContentProgress.blockId == block.id
                    )
                ).first()
                
                if user_progress:
                    progress = {
                        "solvedCount": user_progress.solvedCount,
                        "isCompleted": user_progress.solvedCount > 0
                    }
                else:
                    progress = {
                        "solvedCount": 0,
                        "isCompleted": False
                    }
            
            task = TaskDetail(
                id=block.id,
                title=block.blockTitle or "Задача без названия",
                description=description,
                has_code=block.codeContent is not None,
                code_content=block.codeContent,
                code_language=block.codeLanguage,
                progress=progress
            )
            tasks.append(task)
        
        return tasks
    
    def get_task_by_id(self, task_id: str, user_id: Optional[int] = None) -> Optional[TaskDetail]:
        """Получить задачу по ID"""
        block = self.session.query(ContentBlock).filter(ContentBlock.id == task_id).first()
        if not block:
            return None
        
        description = block.textContent or ""
        if description:
            description = description.replace("\\n", "\n").replace("\\t", "\t")
        
        # Получаем прогресс по задаче если пользователь авторизован
        progress = None
        if user_id:
            user_progress = self.session.query(UserContentProgress).filter(
                UserContentProgress.userId == user_id,
                UserContentProgress.blockId == block.id
            ).first()
            
            if user_progress:
                progress = {
                    "solvedCount": user_progress.solvedCount,
                    "isCompleted": user_progress.solvedCount > 0
                }
            else:
                progress = {
                    "solvedCount": 0,
                    "isCompleted": False
                }
        
        return TaskDetail(
            id=block.id,
            title=block.blockTitle or "Задача без названия",
            description=description,
            has_code=block.codeContent is not None,
            code_content=block.codeContent,
            code_language=block.codeLanguage,
            progress=progress
        )
    
    def get_topic_stats(self, topic: Topic, user_id: Optional[int] = None) -> Optional[TopicStats]:
        """Получить статистику по теме"""
        if not user_id:
            return None
        
        # Получаем все задачи для данной темы
        tasks = self.get_topic_tasks(topic, user_id)
        
        total_tasks = len(tasks)
        completed_tasks = sum(1 for task in tasks if task.progress and task.progress["isCompleted"])
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return TopicStats(
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            completion_rate=float(completion_rate)
        )
    
    def get_available_technologies(self) -> List[str]:
        """Получить список доступных технологий"""
        return get_available_technologies() 