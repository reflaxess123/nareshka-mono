from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime

from ..database import get_db
from ..mindmap_config import get_all_topics, get_topic_config

router = APIRouter(prefix="/api/mindmap", tags=["mindmap"])

@router.get("/generate")
async def generate_mindmap(
    db: Session = Depends(get_db),
    structure_type: str = "topics",
    difficulty_filter: Optional[str] = None,
    topic_filter: Optional[str] = None
) -> Dict[str, Any]:
    try:
        mindmap_data = generate_topic_based_mindmap(
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
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации mindmap: {str(e)}")

def generate_topic_based_mindmap(
    difficulty_filter: Optional[str] = None,
    topic_filter: Optional[str] = None
) -> Dict[str, Any]:
    
    # Используем конфигурацию из отдельного файла
    md_topics = get_all_topics()
    
    nodes = []
    edges = []
    
    nodes.append({
        "id": "center",
        "type": "center",
        "position": {"x": 500, "y": 400},
        "data": {
            "title": "JavaScript Skills",
            "description": "Изучение JavaScript",
            "type": "center"
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
                "type": "topic"
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
        }
    }

@router.get("/topic/{topic_key}/tasks")
async def get_topic_tasks(
    topic_key: str,
    db: Session = Depends(get_db),
    difficulty_filter: Optional[str] = None
) -> Dict[str, Any]:
    try:
        topic_config = get_topic_config(topic_key)
        if not topic_config:
            raise HTTPException(status_code=404, detail=f"Topic '{topic_key}' not found")
        
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
            
            task = {
                "id": block.id,
                "title": block.blockTitle or "Задача без названия",
                "description": description
            }
            tasks.append(task)
        
        return {
            "success": True,
            "topic": {
                "key": topic_key,
                "title": topic_config['title'],
                "icon": topic_config['icon'],
                "color": topic_config['color'],
                "description": topic_config['description']
            },
            "tasks": tasks
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки задач: {str(e)}") 