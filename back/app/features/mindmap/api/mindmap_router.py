"""API роутер для работы с ментальными картами"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.features.mindmap.services.mindmap_service import MindMapService
from app.shared.database import get_session
from app.features.mindmap.dto.responses import (
    MindMapResponse,
    TechnologiesResponse,
    TopicTasksResponse,
    TaskDetailResponseWrapper,
    HealthResponse,
)
from app.features.mindmap.exceptions.mindmap_exceptions import (
    TechnologyNotSupportedError,
    TopicNotFoundError,
    TaskNotFoundError,
)
from app.shared.dependencies import get_current_user_id_optional

logger = logging.getLogger(__name__)

router = APIRouter(tags=["mindmap"])


def get_mindmap_service(db: Session = Depends(get_session)) -> MindMapService:
    """Dependency injection для MindMapService"""
    from app.features.mindmap.repositories.mindmap_repository import MindMapRepository
    
    repository = MindMapRepository(db)
    return MindMapService(repository)


@router.get("/generate", response_model=MindMapResponse)
async def generate_mindmap(
    structure_type: str = Query(default="topics", description="Тип структуры mindmap"),
    technology: str = Query(default="javascript", description="Технология"),
    difficulty_filter: Optional[str] = Query(
        default=None, description="Фильтр по сложности"
    ),
    topic_filter: Optional[str] = Query(default=None, description="Фильтр по теме"),
    user_id: Optional[str] = Depends(get_current_user_id_optional),
    mindmap_service: MindMapService = Depends(get_mindmap_service),
):
    """Генерация данных для mindmap"""
    logger.info(f"API: Генерация mindmap для технологии {technology}")
    
    try:
        # Преобразуем user_id в int если есть
        user_id_int = int(user_id) if user_id else None
        
        # Генерируем mindmap
        mindmap_data = mindmap_service.generate_mindmap(
            user_id=user_id_int,
            technology=technology,
            difficulty_filter=difficulty_filter,
            topic_filter=topic_filter,
        )
        
        logger.info(f"API: Mindmap успешно сгенерирован для {technology}")
        return mindmap_data

    except TechnologyNotSupportedError as e:
        logger.warning(f"API: Неподдерживаемая технология: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"API: Ошибка при генерации mindmap: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при генерации mindmap")


@router.get("/technologies", response_model=TechnologiesResponse)
async def get_available_technologies(
    mindmap_service: MindMapService = Depends(get_mindmap_service),
):
    """Получить доступные технологии"""
    logger.info("API: Получение доступных технологий")
    
    try:
        technologies = mindmap_service.get_available_technologies()
        logger.info("API: Технологии успешно получены")
        return technologies

    except Exception as e:
        logger.error(f"API: Ошибка при получении технологий: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении технологий")


@router.get("/topic/{topic_key}/tasks", response_model=TopicTasksResponse)
async def get_topic_tasks(
    topic_key: str,
    technology: str = Query(default="javascript", description="Технология"),
    difficulty_filter: Optional[str] = Query(
        default=None, description="Фильтр по сложности"
    ),
    user_id: Optional[str] = Depends(get_current_user_id_optional),
    mindmap_service: MindMapService = Depends(get_mindmap_service),
):
    """Получить задачи по теме"""
    logger.info(f"API: Получение задач для топика {topic_key}")
    
    try:
        # Преобразуем user_id в int если есть
        user_id_int = int(user_id) if user_id else None
        
        topic_with_tasks = mindmap_service.get_topic_with_tasks(
            topic_key=topic_key,
            user_id=user_id_int,
            technology=technology,
            difficulty_filter=difficulty_filter,
        )
        
        logger.info(f"API: Задачи для топика {topic_key} успешно получены")
        return topic_with_tasks

    except TopicNotFoundError as e:
        logger.warning(f"API: Топик не найден: {e}")
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        logger.error(f"API: Ошибка при получении задач топика: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении задач")


@router.get("/task/{task_id}", response_model=TaskDetailResponseWrapper)
async def get_task_detail(
    task_id: str,
    user_id: Optional[str] = Depends(get_current_user_id_optional),
    mindmap_service: MindMapService = Depends(get_mindmap_service),
):
    """Получить детали задачи"""
    logger.info(f"API: Получение деталей задачи {task_id}")
    
    try:
        # Преобразуем user_id в int если есть
        user_id_int = int(user_id) if user_id else None
        
        task_detail = mindmap_service.get_task_detail(
            task_id=task_id,
            user_id=user_id_int,
        )
        
        logger.info(f"API: Детали задачи {task_id} успешно получены")
        return task_detail

    except TaskNotFoundError as e:
        logger.warning(f"API: Задача не найдена: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"API: Ошибка при получении деталей задачи: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении деталей задачи")


@router.get("/health", response_model=HealthResponse)
async def health_check(
    mindmap_service: MindMapService = Depends(get_mindmap_service),
):
    """Проверка здоровья модуля"""
    logger.info("API: Проверка здоровья mindmap модуля")
    
    try:
        health_status = mindmap_service.get_health_status()
        logger.info("API: Проверка здоровья завершена")
        return health_status

    except Exception as e:
        logger.error(f"API: Ошибка при проверке здоровья: {e}")
        return HealthResponse(status="unhealthy", module="mindmap") 


@router.get("/debug/classes-tasks")
async def debug_classes_tasks(
    session: Session = Depends(get_session),
):
    """Debug endpoint для проверки задач по классам"""
    from app.shared.models.content_models import ContentBlock, ContentFile
    from sqlalchemy import and_
    
    try:
        # Прямой запрос к базе
        results = (
            session.query(ContentBlock, ContentFile)
            .join(ContentFile, ContentBlock.fileId == ContentFile.id)
            .filter(
                ContentBlock.codeContent.isnot(None),
                ContentFile.mainCategory == "JS",
                ContentFile.subCategory == "Classes",
            )
            .all()
        )
        
        tasks = []
        for content_block, content_file in results:
            task = {
                "id": str(content_block.id),
                "blockTitle": content_block.block_title,
                "hasCode": bool(content_block.code_content),
                "codeLength": len(content_block.code_content) if content_block.code_content else 0,
                "mainCategory": content_file.main_category,
                "subCategory": content_file.sub_category,
            }
            tasks.append(task)
        
        return {
            "success": True,
            "tasks": tasks,
            "count": len(tasks)
        }
        
    except Exception as e:
        logger.error(f"Debug error: {e}")
        return {
            "success": False,
            "error": str(e),
            "tasks": [],
            "count": 0
        } 


@router.get("/test-db")
async def test_db(session: Session = Depends(get_session)):
    """Тестовый endpoint для проверки запросов к БД"""
    from app.shared.models.content_models import ContentBlock, ContentFile
    
    try:
        # Простой запрос к ContentFile
        files = session.query(ContentFile).filter(
            ContentFile.mainCategory == "JS",
            ContentFile.subCategory == "Classes"
        ).all()
        
        # Простой запрос к ContentBlock с join
        blocks = session.query(ContentBlock).join(
            ContentFile, ContentBlock.fileId == ContentFile.id
        ).filter(
            ContentFile.mainCategory == "JS",
            ContentFile.subCategory == "Classes"
        ).all()
        
        # Блоки с кодом
        blocks_with_code = session.query(ContentBlock).join(
            ContentFile, ContentBlock.fileId == ContentFile.id
        ).filter(
            ContentBlock.codeContent.isnot(None),
            ContentFile.mainCategory == "JS",
            ContentFile.subCategory == "Classes"
        ).all()
        
        return {
            "success": True,
            "files_count": len(files),
            "blocks_count": len(blocks),
            "blocks_with_code_count": len(blocks_with_code),
            "first_file": {
                "id": files[0].id if files else None,
                "main_category": files[0].main_category if files else None,
                "sub_category": files[0].sub_category if files else None,
            } if files else None,
            "first_block": {
                "id": blocks_with_code[0].id if blocks_with_code else None,
                "block_title": blocks_with_code[0].block_title if blocks_with_code else None,
                "has_code": bool(blocks_with_code[0].code_content) if blocks_with_code else None,
            } if blocks_with_code else None
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        } 


