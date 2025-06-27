from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime

from ..database import get_db
from ..mindmap_config import get_all_topics, get_topic_config
from ..auth import get_current_user_from_session_required
from ..models import ContentBlock, ContentFile, UserContentProgress
from sqlalchemy import func, and_

router = APIRouter(prefix="/api/mindmap", tags=["mindmap"])

@router.get("/generate")
async def generate_mindmap(
    request: Request,
    db: Session = Depends(get_db),
    structure_type: str = "topics",
    difficulty_filter: Optional[str] = None,
    topic_filter: Optional[str] = None
) -> Dict[str, Any]:
    try:
        # Получаем пользователя (если авторизован)
        user = None
        try:
            user = get_current_user_from_session_required(request, db)
        except:
            pass  # Пользователь не авторизован, продолжаем без прогресса

        mindmap_data = generate_topic_based_mindmap(
            db=db,
            user_id=user.id if user else None,
            difficulty_filter=difficulty_filter,
            topic_filter=topic_filter
        )
        
        return {
            "success": True,
            "data": mindmap_data,
            "structure_type": structure_type,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "filters_applied": {
                    "difficulty": difficulty_filter,
                    "topic": topic_filter
                },
                "user_authenticated": user is not None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации mindmap: {str(e)}")

def generate_topic_based_mindmap(
    db: Session,
    user_id: Optional[int] = None,
    difficulty_filter: Optional[str] = None,
    topic_filter: Optional[str] = None
) -> Dict[str, Any]:
    
    # Используем конфигурацию из отдельного файла
    md_topics = get_all_topics()
    
    nodes = []
    edges = []
    
    # Получаем общий прогресс пользователя если авторизован
    overall_progress = None
    if user_id:
        total_tasks_with_code = db.query(func.count(ContentBlock.id)).join(ContentFile).filter(
            ContentBlock.codeContent.isnot(None),
            ContentFile.mainCategory == 'JS'  # Считаем только JavaScript задачи
        ).scalar() or 0
        
        completed_tasks = db.query(func.count(UserContentProgress.id)).filter(
            UserContentProgress.userId == user_id,
            UserContentProgress.solvedCount > 0
        ).join(ContentBlock).join(ContentFile).filter(
            ContentBlock.codeContent.isnot(None),
            ContentFile.mainCategory == 'JS'  # Считаем только JavaScript задачи
        ).scalar() or 0
        
        overall_completion_rate = (completed_tasks / total_tasks_with_code * 100) if total_tasks_with_code > 0 else 0
        
        overall_progress = {
            "totalTasks": total_tasks_with_code,
            "completedTasks": completed_tasks,
            "completionRate": float(overall_completion_rate)
        }
    
    nodes.append({
        "id": "center",
        "type": "center",
        "position": {"x": 500, "y": 400},
        "data": {
            "title": "JavaScript Skills",
            "description": "Изучение JavaScript",
            "type": "center",
            "overallProgress": overall_progress
        }
    })
    
    import math
    radius = 400
    
    active_topics = list(md_topics.items())
    if topic_filter and topic_filter in md_topics:
        active_topics = [(topic_filter, md_topics[topic_filter])]
    
    topic_count = len(active_topics)
    
    for i, (topic_key, topic_config) in enumerate(active_topics):
        angle = (2 * math.pi * i) / topic_count
        x = 500 + radius * math.cos(angle)
        y = 400 + radius * math.sin(angle)
        
        # Получаем прогресс по данной категории если пользователь авторизован
        progress_data = None
        if user_id:
            # Общее количество задач в категории (с кодом)
            total_tasks = db.query(func.count(ContentBlock.id)).join(ContentFile).filter(
                ContentFile.mainCategory == topic_config['mainCategory'],
                ContentFile.subCategory == topic_config['subCategory'],
                ContentBlock.codeContent.isnot(None)
            ).scalar() or 0

            # Количество решённых задач
            completed_tasks = db.query(func.count(UserContentProgress.id)).filter(
                UserContentProgress.userId == user_id,
                UserContentProgress.solvedCount > 0
            ).join(ContentBlock).join(ContentFile).filter(
                ContentFile.mainCategory == topic_config['mainCategory'],
                ContentFile.subCategory == topic_config['subCategory'],
                ContentBlock.codeContent.isnot(None)
            ).scalar() or 0

            # Рассчитываем процент завершения
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

            # Определяем статус
            status = "not_started"
            if completed_tasks > 0:
                if completion_rate >= 100:
                    status = "completed"
                else:
                    status = "in_progress"

            progress_data = {
                "totalTasks": total_tasks,
                "completedTasks": completed_tasks,
                "completionRate": float(completion_rate),
                "status": status
            }
        
        nodes.append({
            "id": f"topic_{topic_key}",
            "type": "topic",
            "position": {"x": x, "y": y},
            "data": {
                "title": topic_config['title'],
                "icon": topic_config['icon'],
                "color": topic_config['color'],
                "description": topic_config['description'],
                "topic_key": topic_key,
                "type": "topic",
                "progress": progress_data
            }
        })
        
        edges.append({
            "id": f"edge_center_{topic_key}",
            "source": "center",
            "target": f"topic_{topic_key}",
            "style": {
                "stroke": topic_config['color'],
                "strokeWidth": 3,
                "strokeOpacity": 0.7
            },
            "animated": True
        })
    
    return {
        "nodes": nodes,
        "edges": edges,
        "layout": "radial",
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "structure_type": "topics_simple",
        "active_topics": len(active_topics),
        "applied_filters": {
            "difficulty": difficulty_filter,
            "topic": topic_filter
        },
        "overall_progress": overall_progress
    }

@router.get("/topic/{topic_key}/tasks")
async def get_topic_tasks(
    topic_key: str,
    request: Request,
    db: Session = Depends(get_db),
    difficulty_filter: Optional[str] = None
) -> Dict[str, Any]:
    try:
        topic_config = get_topic_config(topic_key)
        if not topic_config:
            raise HTTPException(status_code=404, detail=f"Topic '{topic_key}' not found")
        
        # Получаем пользователя (если авторизован)
        user = None
        try:
            user = get_current_user_from_session_required(request, db)
        except:
            pass  # Пользователь не авторизован
        
        from ..models import ContentBlock, ContentFile
        from sqlalchemy import asc, func
        
        query = db.query(ContentBlock).join(ContentFile)
        
        query = query.filter(
            func.lower(ContentFile.mainCategory) == func.lower(topic_config['mainCategory']),
            func.lower(ContentFile.subCategory) == func.lower(topic_config['subCategory'])
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
            if user:
                user_progress = db.query(UserContentProgress).filter(
                    and_(
                        UserContentProgress.userId == user.id,
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
            
            task = {
                "id": block.id,
                "title": block.blockTitle or "Задача без названия",
                "description": description,
                "hasCode": block.codeContent is not None,
                "progress": progress
            }
            tasks.append(task)
        
        # Получаем общую статистику по топику
        topic_stats = None
        if user:
            total_tasks = sum(1 for task in tasks if task["hasCode"])
            completed_tasks = sum(1 for task in tasks if task["progress"] and task["progress"]["isCompleted"] and task["hasCode"])
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            topic_stats = {
                "totalTasks": total_tasks,
                "completedTasks": completed_tasks,
                "completionRate": float(completion_rate)
            }
        
        return {
            "success": True,
            "topic": {
                "key": topic_key,
                "title": topic_config['title'],
                "icon": topic_config['icon'],
                "color": topic_config['color'],
                "description": topic_config['description']
            },
            "tasks": tasks,
            "stats": topic_stats
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки задач: {str(e)}") 