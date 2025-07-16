"""Репозиторий для работы с ментальными картами"""

import logging
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.shared.models.content_models import (
    ContentBlock,
    ContentFile,
)
from app.shared.models.content_models import UserContentProgress
from app.config.mindmap_config import (
    get_available_technologies,
    get_technology_center,
    get_technology_topics,
    get_topic_config,
)
from app.features.mindmap.exceptions.mindmap_exceptions import (
    TechnologyNotSupportedError,
    TopicNotFoundError,
    TaskNotFoundError,
)

logger = logging.getLogger(__name__)


class MindMapRepositoryInterface(ABC):
    """Интерфейс репозитория для работы с mindmap"""

    @abstractmethod
    def get_technology_center(self, technology: str) -> Optional[Dict[str, Any]]:
        """Получить центральный узел технологии"""
        pass

    @abstractmethod
    def get_technology_topics(self, technology: str) -> List[Dict[str, Any]]:
        """Получить все топики для технологии"""
        pass

    @abstractmethod
    def get_topic_config(self, topic_key: str, technology: str) -> Optional[Dict[str, Any]]:
        """Получить конфигурацию топика"""
        pass

    @abstractmethod
    def get_overall_progress(self, user_id: int, technology: str) -> Optional[Dict[str, Any]]:
        """Получить общий прогресс пользователя по технологии"""
        pass

    @abstractmethod
    def get_topic_progress(self, user_id: int, topic_key: str, technology: str) -> Optional[Dict[str, Any]]:
        """Получить прогресс пользователя по теме"""
        pass

    @abstractmethod
    def get_topic_tasks(self, topic_key: str, technology: str, user_id: Optional[int] = None, difficulty_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Получить задачи для топика"""
        pass

    @abstractmethod
    def get_task_by_id(self, task_id: str, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Получить задачу по ID"""
        pass

    @abstractmethod
    def get_topic_stats(self, topic_key: str, technology: str, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Получить статистику по топику"""
        pass

    @abstractmethod
    def get_available_technologies(self) -> List[str]:
        """Получить список доступных технологий"""
        pass


class MindMapRepository(MindMapRepositoryInterface):
    """Репозиторий для работы с ментальными картами"""

    def __init__(self, session: Session):
        self.session = session

    def get_technology_center(self, technology: str) -> Optional[Dict[str, Any]]:
        """Получить центральный узел технологии"""
        logger.info(f"Получение центра технологии: {technology}")
        
        config = get_technology_center(technology)
        if not config:
            logger.warning(f"Технология не найдена: {technology}")
            return None

        return {
            "technology": technology,
            "display_name": config["title"],
            "description": config["description"],
            "icon": config["icon"],
            "color": config["color"],
            "main_category": config["mainCategory"],
        }

    def get_technology_topics(self, technology: str) -> List[Dict[str, Any]]:
        """Получить все топики для технологии"""
        logger.info(f"Получение топиков для технологии: {technology}")
        
        topics_config = get_technology_topics(technology)
        if not topics_config:
            logger.warning(f"Топики не найдены для технологии: {technology}")
            return []

        topics = []
        for key, config in topics_config.items():
            topic = {
                "key": key,
                "title": config["title"],
                "description": config["description"],
                "icon": config["icon"],
                "color": config["color"],
                "main_category": config["mainCategory"],
                "sub_category": config["subCategory"],
                "technology": technology,
            }
            topics.append(topic)

        logger.info(f"Найдено {len(topics)} топиков для технологии {technology}")
        return topics

    def get_topic_config(self, topic_key: str, technology: str) -> Optional[Dict[str, Any]]:
        """Получить конфигурацию топика"""
        logger.info(f"Получение конфигурации топика: {topic_key} для {technology}")
        
        config = get_topic_config(topic_key, technology)
        
        if not config:
            logger.warning(f"Конфигурация топика не найдена: {topic_key}")
            return None

        return {
            "key": topic_key,
            "title": config["title"],
            "description": config["description"],
            "icon": config["icon"],
            "color": config["color"],
            "main_category": config["mainCategory"],
            "sub_category": config["subCategory"],
            "technology": technology,
        }

    def get_overall_progress(self, user_id: int, technology: str) -> Optional[Dict[str, Any]]:
        """Получить общий прогресс пользователя по технологии"""
        logger.info(f"Получение общего прогресса пользователя {user_id} по технологии {technology}")
        
        try:
            tech_center = self.get_technology_center(technology)
            if not tech_center:
                return None

            main_category = tech_center["main_category"]

            # Получаем общее количество задач с кодом для данной технологии
            total_tasks = (
                self.session.query(func.count(ContentBlock.id))
                .join(ContentFile, ContentBlock.fileId == ContentFile.id)
                .filter(
                    ContentBlock.codeContent.isnot(None),
                    func.lower(ContentFile.mainCategory) == func.lower(main_category),
                )
                .scalar()
                or 0
            )

            # Получаем количество решенных задач
            completed_tasks = (
                self.session.query(func.count(UserContentProgress.id))
                .join(ContentBlock, UserContentProgress.blockId == ContentBlock.id)
                .join(ContentFile, ContentBlock.fileId == ContentFile.id)
                .filter(
                    UserContentProgress.userId == user_id,
                    UserContentProgress.solvedCount > 0,
                    ContentBlock.codeContent.isnot(None),
                    func.lower(ContentFile.mainCategory) == func.lower(main_category),
                )
                .scalar()
                or 0
            )

            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

            progress = {
                "totalTasks": total_tasks,
                "completedTasks": completed_tasks,
                "completionRate": round(completion_rate, 1),
                "status": "completed" if completion_rate == 100 else "in_progress" if completion_rate > 0 else "not_started"
            }

            logger.info(f"Общий прогресс пользователя {user_id}: {completed_tasks}/{total_tasks} ({completion_rate:.1f}%)")
            return progress

        except Exception as e:
            logger.error(f"Ошибка при получении общего прогресса: {e}")
            return None

    def get_topic_progress(self, user_id: int, topic_key: str, technology: str) -> Optional[Dict[str, Any]]:
        """Получить прогресс пользователя по теме"""
        logger.info(f"Получение прогресса по топику {topic_key} для пользователя {user_id}")
        
        try:
            topic_config = self.get_topic_config(topic_key, technology)
            if not topic_config:
                return None

            main_category = topic_config["main_category"]
            sub_category = topic_config["sub_category"]

            # Получаем общее количество задач в топике
            total_tasks = (
                self.session.query(func.count(ContentBlock.id))
                .join(ContentFile, ContentBlock.fileId == ContentFile.id)
                .filter(
                    ContentBlock.codeContent.isnot(None),
                    func.lower(ContentFile.mainCategory) == func.lower(main_category),
                    func.lower(ContentFile.subCategory) == func.lower(sub_category),
                )
                .scalar()
                or 0
            )

            # Получаем количество решенных задач в топике
            completed_tasks = (
                self.session.query(func.count(UserContentProgress.id))
                .join(ContentBlock, UserContentProgress.blockId == ContentBlock.id)
                .join(ContentFile, ContentBlock.fileId == ContentFile.id)
                .filter(
                    UserContentProgress.userId == user_id,
                    UserContentProgress.solvedCount > 0,
                    ContentBlock.codeContent.isnot(None),
                    func.lower(ContentFile.mainCategory) == func.lower(main_category),
                    func.lower(ContentFile.subCategory) == func.lower(sub_category),
                )
                .scalar()
                or 0
            )

            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

            progress = {
                "totalTasks": total_tasks,
                "completedTasks": completed_tasks,
                "completionRate": round(completion_rate, 1),
                "status": "completed" if completion_rate == 100 else "in_progress" if completion_rate > 0 else "not_started"
            }

            logger.info(f"Прогресс по топику {topic_key}: {completed_tasks}/{total_tasks} ({completion_rate:.1f}%)")
            return progress

        except Exception as e:
            logger.error(f"Ошибка при получении прогресса по топику: {e}")
            return None

    def get_topic_tasks(self, topic_key: str, technology: str, user_id: Optional[int] = None, difficulty_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Получить задачи для топика"""
        logger.info(f"Получение задач для топика {topic_key}, технология {technology}")
        
        try:
            topic_config = self.get_topic_config(topic_key, technology)
            if not topic_config:
                logger.warning(f"Конфигурация топика не найдена: {topic_key}")
                return []

            main_category = topic_config["main_category"]
            sub_category = topic_config["sub_category"]
            
            logger.info(f"Поиск задач для категории: {main_category}, подкатегории: {sub_category}")

            # Используем простой join как в content_repository с func.lower()
            results = (
                self.session.query(ContentBlock)
                .join(ContentFile)
                .filter(
                    ContentBlock.codeContent.isnot(None),
                    func.lower(ContentFile.mainCategory) == func.lower(main_category),
                    func.lower(ContentFile.subCategory) == func.lower(sub_category),
                )
                .all()
            )
            
            logger.info(f"Найдено {len(results)} блоков для топика {topic_key}")
            
            tasks = []
            for content_block in results:
                    # Получаем прогресс если пользователь указан
                    progress = None
                    if user_id:
                        user_progress = (
                            self.session.query(UserContentProgress)
                            .filter(
                                UserContentProgress.userId == user_id,
                                UserContentProgress.blockId == content_block.id,
                            )
                            .first()
                        )
                        
                        if user_progress:
                            progress = {
                                "solvedCount": user_progress.solvedCount,
                                "isCompleted": user_progress.solvedCount > 0,
                            }

                    task = {
                        "id": str(content_block.id),
                        "title": content_block.blockTitle or f"Задача {content_block.id}",
                        "description": content_block.textContent or "",
                        "hasCode": bool(content_block.codeContent),
                        "progress": progress,
                    }
                    tasks.append(task)

            logger.info(f"Найдено {len(tasks)} задач для топика {topic_key}")
            return tasks

        except Exception as e:
            logger.error(f"Ошибка при получении задач для топика: {e}")
            return []

    def get_task_by_id(self, task_id: str, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Получить задачу по ID"""
        logger.info(f"Получение задачи по ID: {task_id}")
        
        try:
            content_block = (
                self.session.query(ContentBlock)
                .filter(ContentBlock.id == int(task_id))
                .first()
            )

            if not content_block:
                logger.warning(f"Задача не найдена: {task_id}")
                return None

            # Получаем прогресс если пользователь указан
            progress = None
            if user_id:
                user_progress = (
                    self.session.query(UserContentProgress)
                    .filter(
                        UserContentProgress.userId == user_id,
                        UserContentProgress.blockId == content_block.id,
                    )
                    .first()
                )
                
                if user_progress:
                    progress = {
                        "solvedCount": user_progress.solved_count,
                        "isCompleted": user_progress.solved_count > 0,
                    }

            task = {
                "id": str(content_block.id),
                "title": content_block.block_title or f"Задача {content_block.id}",
                "description": content_block.text_content or "",
                "hasCode": bool(content_block.code_content),
                "codeContent": content_block.code_content,
                "codeLanguage": "javascript",  # Default для mindmap
                "progress": progress,
            }

            logger.info(f"Задача найдена: {task_id}")
            return task

        except Exception as e:
            logger.error(f"Ошибка при получении задачи: {e}")
            return None

    def get_topic_stats(self, topic_key: str, technology: str, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Получить статистику по топику"""
        logger.info(f"Получение статистики по топику {topic_key}")
        
        try:
            topic_config = self.get_topic_config(topic_key, technology)
            if not topic_config:
                return None

            main_category = topic_config["main_category"]
            sub_category = topic_config["sub_category"]

            # Общее количество задач
            total_tasks = (
                self.session.query(func.count(ContentBlock.id))
                .join(ContentFile, ContentBlock.fileId == ContentFile.id)
                .filter(
                    ContentBlock.codeContent.isnot(None),
                    func.lower(ContentFile.mainCategory) == func.lower(main_category),
                    func.lower(ContentFile.subCategory) == func.lower(sub_category),
                )
                .scalar()
                or 0
            )

            completed_tasks = 0
            if user_id:
                completed_tasks = (
                    self.session.query(func.count(UserContentProgress.id))
                    .join(ContentBlock, UserContentProgress.blockId == ContentBlock.id)
                    .join(ContentFile, ContentBlock.fileId == ContentFile.id)
                    .filter(
                        UserContentProgress.userId == user_id,
                        UserContentProgress.solvedCount > 0,
                        ContentBlock.codeContent.isnot(None),
                        func.lower(ContentFile.mainCategory) == func.lower(main_category),
                        func.lower(ContentFile.subCategory) == func.lower(sub_category),
                    )
                    .scalar()
                    or 0
                )

            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

            stats = {
                "totalTasks": total_tasks,
                "completedTasks": completed_tasks,
                "completionRate": round(completion_rate, 1),
            }

            logger.info(f"Статистика топика {topic_key}: {completed_tasks}/{total_tasks}")
            return stats

        except Exception as e:
            logger.error(f"Ошибка при получении статистики топика: {e}")
            return None

    def get_available_technologies(self) -> List[str]:
        """Получить список доступных технологий"""
        logger.info("Получение списка доступных технологий")
        
        try:
            technologies = get_available_technologies()
            logger.info(f"Найдено {len(technologies)} технологий")
            return technologies
        except Exception as e:
            logger.error(f"Ошибка при получении технологий: {e}")
            return [] 



