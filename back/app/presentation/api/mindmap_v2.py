from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.application.dto.mindmap_dto import (
    HealthResponse,
    MindMapDataResponse,
    MindMapEdgeResponse,
    MindMapNodeResponse,
    MindMapResponse,
    TaskDetailResponse,
    TaskDetailResponseWrapper,
    TaskProgressResponse,
    TaskResponse,
    TechnologiesDataResponse,
    TechnologiesResponse,
    TechnologyConfigResponse,
    TopicResponse,
    TopicStatsResponse,
    TopicTasksResponse,
)
from app.application.services.mindmap_service import MindMapService
from app.shared.dependencies import get_current_user_optional, get_mindmap_service

router = APIRouter(tags=["mindmap"])


@router.get("/generate", response_model=MindMapResponse)
async def generate_mindmap(
    request: Request,
    structure_type: str = Query(default="topics", description="Тип структуры mindmap"),
    technology: str = Query(default="javascript", description="Технология"),
    difficulty_filter: Optional[str] = Query(
        default=None, description="Фильтр по сложности"
    ),
    topic_filter: Optional[str] = Query(default=None, description="Фильтр по теме"),
    mindmap_service: MindMapService = Depends(get_mindmap_service),
    user=Depends(get_current_user_optional),
):
    """Генерация данных для mindmap"""
    try:
        # Пользователь получен через DI (может быть None если не авторизован)

        # Генерируем mindmap
        mindmap_data = mindmap_service.generate_mindmap(
            user_id=user.id if user else None,
            technology=technology,
            difficulty_filter=difficulty_filter,
            topic_filter=topic_filter,
        )

        # Преобразуем в DTO
        nodes = [
            MindMapNodeResponse(
                id=node.id, type=node.type, position=node.position, data=node.data
            )
            for node in mindmap_data.nodes
        ]

        edges = [
            MindMapEdgeResponse(
                id=edge.id,
                source=edge.source,
                target=edge.target,
                style=edge.style,
                animated=edge.animated,
            )
            for edge in mindmap_data.edges
        ]

        data = MindMapDataResponse(
            nodes=nodes,
            edges=edges,
            layout=mindmap_data.layout,
            total_nodes=mindmap_data.total_nodes,
            total_edges=mindmap_data.total_edges,
            structure_type=mindmap_data.structure_type,
            active_topics=mindmap_data.active_topics,
            applied_filters=mindmap_data.applied_filters,
            overall_progress=mindmap_data.overall_progress,
        )

        return MindMapResponse(
            success=True,
            data=data.model_dump(),
            structure_type=structure_type,
            metadata={
                "generated_at": datetime.now().isoformat(),
                "technology": technology,
                "filters_applied": {
                    "difficulty": difficulty_filter,
                    "topic": topic_filter,
                },
                "user_authenticated": user is not None,
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка генерации mindmap: {str(e)}"
        )


@router.get("/technologies", response_model=TechnologiesResponse)
async def get_available_technologies(
    mindmap_service: MindMapService = Depends(get_mindmap_service),
):
    """Получить список доступных технологий для mindmap"""
    try:
        technologies_data = mindmap_service.get_available_technologies()

        # Преобразуем конфигурации в DTO
        configs = {}
        for tech, config in technologies_data["configs"].items():
            configs[tech] = TechnologyConfigResponse(
                title=config["title"],
                description=config["description"],
                icon=config["icon"],
                color=config["color"],
            )

        data = TechnologiesDataResponse(
            technologies=technologies_data["technologies"], configs=configs
        )

        return TechnologiesResponse(success=True, data=data.model_dump())

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка получения технологий: {str(e)}"
        )


@router.get("/topic/{topic_key}/tasks", response_model=TopicTasksResponse)
async def get_topic_tasks(
    topic_key: str,
    request: Request,
    technology: str = Query(default="javascript", description="Технология"),
    difficulty_filter: Optional[str] = Query(
        default=None, description="Фильтр по сложности"
    ),
    mindmap_service: MindMapService = Depends(get_mindmap_service),
    user=Depends(get_current_user_optional),
):
    """Получить задачи для конкретной темы"""
    try:
        # Пользователь получен через DI (может быть None если не авторизован)

        # Получаем тему с задачами
        topic_with_tasks = mindmap_service.get_topic_with_tasks(
            topic_key=topic_key,
            user_id=user.id if user else None,
            technology=technology,
            difficulty_filter=difficulty_filter,
        )

        # Преобразуем в DTO
        topic_dto = TopicResponse(
            key=topic_with_tasks.topic.key,
            title=topic_with_tasks.topic.title,
            icon=topic_with_tasks.topic.icon,
            color=topic_with_tasks.topic.color,
            description=topic_with_tasks.topic.description,
        )

        tasks_dto = []
        for task in topic_with_tasks.tasks:
            progress_dto = None
            if task.progress:
                progress_dto = TaskProgressResponse(
                    solvedCount=task.progress["solvedCount"],
                    isCompleted=task.progress["isCompleted"],
                )

            task_dto = TaskResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                hasCode=task.has_code,
                progress=progress_dto,
            )
            tasks_dto.append(task_dto)

        stats_dto = None
        if topic_with_tasks.stats:
            stats_dto = TopicStatsResponse(
                totalTasks=topic_with_tasks.stats.total_tasks,
                completedTasks=topic_with_tasks.stats.completed_tasks,
                completionRate=topic_with_tasks.stats.progress_percentage,
            )

        return TopicTasksResponse(
            success=True, topic=topic_dto, tasks=tasks_dto, stats=stats_dto
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки задач: {str(e)}")


@router.get("/task/{task_id}", response_model=TaskDetailResponseWrapper)
async def get_task_detail(
    task_id: str,
    request: Request,
    mindmap_service: MindMapService = Depends(get_mindmap_service),
    user=Depends(get_current_user_optional),
):
    """Получить детали задачи"""
    try:
        # Пользователь получен через DI (может быть None если не авторизован)

        # Получаем детали задачи
        task = mindmap_service.get_task_detail(task_id, user.id if user else None)

        # Преобразуем в DTO
        progress_dto = None
        if task.progress:
            progress_dto = TaskProgressResponse(
                solvedCount=task.progress["solvedCount"],
                isCompleted=task.progress["isCompleted"],
            )

        task_dto = TaskDetailResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            hasCode=task.has_code,
            codeContent=task.code_content,
            codeLanguage=task.code_language,
            progress=progress_dto,
        )

        return TaskDetailResponseWrapper(success=True, task=task_dto)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки задачи: {str(e)}")


@router.get("/health", response_model=HealthResponse)
async def health_check(mindmap_service: MindMapService = Depends(get_mindmap_service)):
    """Health check для mindmap модуля"""
    try:
        health_status = mindmap_service.get_health_status()
        return HealthResponse(
            status=health_status["status"], module=health_status["module"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
