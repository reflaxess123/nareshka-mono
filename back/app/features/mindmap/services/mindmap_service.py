"""Сервис для работы с ментальными картами"""

import logging
import math
from typing import Any, Dict, List, Optional

from app.features.mindmap.repositories.mindmap_repository import MindMapRepository
from app.features.mindmap.dto.responses import (
    MindMapResponse,
    MindMapDataResponse,
    MindMapNodeResponse,
    MindMapEdgeResponse,
    TechnologiesResponse,
    TechnologiesDataResponse,
    TechnologyConfigResponse,
    TopicTasksResponse,
    TopicResponse,
    TaskResponse,
    TaskProgressResponse,
    TopicStatsResponse,
    TaskDetailResponseWrapper,
    TaskDetailResponse,
    HealthResponse,
)
from app.features.mindmap.exceptions.mindmap_exceptions import (
    TechnologyNotSupportedError,
    TopicNotFoundError,
    TaskNotFoundError,
)

logger = logging.getLogger(__name__)


class MindMapService:
    """Сервис для работы с ментальными картами"""

    def __init__(self, mindmap_repository: MindMapRepository):
        self.mindmap_repository = mindmap_repository

    def generate_mindmap(
        self,
        user_id: Optional[int] = None,
        technology: str = "javascript",
        difficulty_filter: Optional[str] = None,
        topic_filter: Optional[str] = None,
    ) -> MindMapResponse:
        """Генерация данных для mindmap"""
        logger.info(f"Генерация mindmap для технологии {technology}, пользователь: {user_id}")
        
        try:
            # Получаем центральный узел технологии
            tech_center = self.mindmap_repository.get_technology_center(technology)
            if not tech_center:
                raise TechnologyNotSupportedError(technology)

            # Получаем общий прогресс пользователя если авторизован
            overall_progress = None
            if user_id:
                overall_progress = self.mindmap_repository.get_overall_progress(user_id, technology)

            # Получаем топики для технологии
            all_topics = self.mindmap_repository.get_technology_topics(technology)

            # Применяем фильтры
            active_topics = all_topics
            if topic_filter:
                active_topics = [topic for topic in all_topics if topic["key"] == topic_filter]

            # Создаем узлы и связи
            nodes = []
            edges = []

            # Центральный узел
            center_node = MindMapNodeResponse(
                id="center",
                type="center",
                position={"x": 500.0, "y": 400.0},
                data={
                    "title": tech_center["display_name"],
                    "description": tech_center["description"],
                    "icon": tech_center["icon"],
                    "color": tech_center["color"],
                    "type": "center",
                    "technology": technology,
                    "overallProgress": overall_progress,
                },
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
                topic_progress = None
                if user_id:
                    topic_progress = self.mindmap_repository.get_topic_progress(
                        user_id, topic["key"], technology
                    )

                # Создаем узел топика
                topic_node = MindMapNodeResponse(
                    id=f"topic_{topic['key']}",
                    type="topic",
                    position={"x": x, "y": y},
                    data={
                        "title": topic["title"],
                        "icon": topic["icon"],
                        "color": topic["color"],
                        "description": topic["description"],
                        "topic_key": topic["key"],
                        "type": "topic",
                        "progress": topic_progress,
                    },
                )
                nodes.append(topic_node)

                # Создаем связь с центральным узлом
                edge = MindMapEdgeResponse(
                    id=f"edge_center_to_{topic['key']}",
                    source="center",
                    target=f"topic_{topic['key']}",
                    style={"stroke": "#999", "strokeWidth": 2},
                    animated=False,
                )
                edges.append(edge)

            # Подготавливаем данные ответа
            mindmap_data = MindMapDataResponse(
                nodes=nodes,
                edges=edges,
                layout="radial",
                total_nodes=len(nodes),
                total_edges=len(edges),
                structure_type="topics",
                active_topics=len(active_topics),
                applied_filters={
                    "difficulty": difficulty_filter,
                    "topic": topic_filter,
                },
                overall_progress=overall_progress,
            )

            metadata = {
                "technology": technology,
                "generated_at": "now",
                "user_id": user_id,
                "filters_applied": bool(difficulty_filter or topic_filter),
            }

            logger.info(f"Mindmap сгенерирован: {len(nodes)} узлов, {len(edges)} связей")
            
            return MindMapResponse(
                success=True,
                data=mindmap_data,
                structure_type="topics",
                metadata=metadata,
            )

        except TechnologyNotSupportedError:
            raise
        except Exception as e:
            logger.error(f"Ошибка при генерации mindmap: {e}")
            raise

    def get_available_technologies(self) -> TechnologiesResponse:
        """Получить доступные технологии"""
        logger.info("Получение доступных технологий")
        
        try:
            tech_list = self.mindmap_repository.get_available_technologies()
            
            # Получаем конфигурации для каждой технологии
            configs = {}
            for tech in tech_list:
                tech_center = self.mindmap_repository.get_technology_center(tech)
                if tech_center:
                    configs[tech] = TechnologyConfigResponse(
                        title=tech_center["display_name"],
                        description=tech_center["description"],
                        icon=tech_center["icon"],
                        color=tech_center["color"],
                    )

            data = TechnologiesDataResponse(
                technologies=tech_list,
                configs=configs,
            )

            logger.info(f"Получено {len(tech_list)} технологий")
            return TechnologiesResponse(success=True, data=data)

        except Exception as e:
            logger.error(f"Ошибка при получении технологий: {e}")
            raise

    def get_topic_with_tasks(
        self,
        topic_key: str,
        user_id: Optional[int] = None,
        technology: str = "javascript",
        difficulty_filter: Optional[str] = None,
    ) -> TopicTasksResponse:
        """Получить топик с задачами"""
        logger.info(f"Получение задач для топика {topic_key}, технология {technology}")
        
        try:
            # Получаем конфигурацию топика
            topic_config = self.mindmap_repository.get_topic_config(topic_key, technology)
            if not topic_config:
                raise TopicNotFoundError(topic_key, technology)

            # Получаем прогресс по топику если пользователь авторизован
            topic_progress = None
            if user_id:
                topic_progress = self.mindmap_repository.get_topic_progress(
                    user_id, topic_key, technology
                )

            # Создаем объект топика
            topic = TopicResponse(
                key=topic_config["key"],
                title=topic_config["title"],
                icon=topic_config["icon"],
                color=topic_config["color"],
                description=topic_config["description"],
                progress=topic_progress,
            )

            # Получаем задачи для топика
            task_data = self.mindmap_repository.get_topic_tasks(
                topic_key, technology, user_id, difficulty_filter
            )

            tasks = []
            for task in task_data:
                task_progress = None
                if task.get("progress"):
                    task_progress = TaskProgressResponse(
                        solvedCount=task["progress"]["solvedCount"],
                        isCompleted=task["progress"]["isCompleted"],
                    )

                task_obj = TaskResponse(
                    id=task["id"],
                    title=task["title"],
                    description=task["description"],
                    hasCode=task["hasCode"],
                    progress=task_progress,
                )
                tasks.append(task_obj)

            # Получаем статистику
            stats = None
            if user_id:
                stats_data = self.mindmap_repository.get_topic_stats(topic_key, technology, user_id)
                if stats_data:
                    stats = TopicStatsResponse(
                        totalTasks=stats_data["totalTasks"],
                        completedTasks=stats_data["completedTasks"],
                        completionRate=stats_data["completionRate"],
                    )

            logger.info(f"Получено {len(tasks)} задач для топика {topic_key}")
            return TopicTasksResponse(
                success=True,
                topic=topic,
                tasks=tasks,
                stats=stats,
            )

        except TopicNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Ошибка при получении задач топика: {e}")
            raise

    def get_task_detail(self, task_id: str, user_id: Optional[int] = None) -> TaskDetailResponseWrapper:
        """Получить детали задачи"""
        logger.info(f"Получение деталей задачи {task_id}")
        
        try:
            task_data = self.mindmap_repository.get_task_by_id(task_id, user_id)
            if not task_data:
                raise TaskNotFoundError(task_id)

            # Создаем прогресс если есть данные
            task_progress = None
            if task_data.get("progress"):
                task_progress = TaskProgressResponse(
                    solvedCount=task_data["progress"]["solvedCount"],
                    isCompleted=task_data["progress"]["isCompleted"],
                )

            task_detail = TaskDetailResponse(
                id=task_data["id"],
                title=task_data["title"],
                description=task_data["description"],
                hasCode=task_data["hasCode"],
                codeContent=task_data.get("codeContent"),
                codeLanguage=task_data.get("codeLanguage"),
                progress=task_progress,
            )

            logger.info(f"Детали задачи {task_id} получены")
            return TaskDetailResponseWrapper(success=True, task=task_detail)

        except TaskNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Ошибка при получении деталей задачи: {e}")
            raise

    def get_health_status(self) -> HealthResponse:
        """Получить статус здоровья модуля"""
        logger.info("Проверка здоровья mindmap модуля")
        
        try:
            # Проверяем доступность технологий
            technologies = self.mindmap_repository.get_available_technologies()
            
            status = "healthy" if len(technologies) > 0 else "unhealthy"
            
            return HealthResponse(
                status=status,
                module="mindmap",
            )

        except Exception as e:
            logger.error(f"Ошибка при проверке здоровья: {e}")
            return HealthResponse(
                status="unhealthy",
                module="mindmap",
            ) 


