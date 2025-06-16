from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import json
from datetime import datetime

from ..database import get_db

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
    
    md_topics = {
        'closures': {
            'title': 'Замыкания',
            'icon': '🔒',
            'color': '#8B5CF6',
            'description': 'Функции и области видимости'
        },
        'throttle_debounce': {
            'title': 'Тротлы и дебаунсы',
            'icon': '⏱️',
            'color': '#F97316',
            'description': 'Оптимизация производительности'
        },
        'custom_functions': {
            'title': 'Кастомные методы и функции',
            'icon': '⚡',
            'color': '#3B82F6',
            'description': 'Создание собственных функций и методов'
        },
        'time': {
            'title': 'Часовая',
            'icon': '🕐',
            'color': '#06B6D4',
            'description': 'Работа с временем и датами'
        },
        'arrays': {
            'title': 'Массивы',
            'icon': '📝',
            'color': '#F59E0B',
            'description': 'Работа с массивами и их методами'
        },
        'promises': {
            'title': 'Промисы',
            'icon': '🔄',
            'color': '#06B6D4',
            'description': 'Асинхронная работа и промисы'
        },
        'strings': {
            'title': 'Строки',
            'icon': '🔤',
            'color': '#8B5CF6',
            'description': 'Обработка строк и регулярные выражения'
        },
        'objects': {
            'title': 'Объекты',
            'icon': '📦',
            'color': '#84CC16',
            'description': 'Работа с объектами и их свойствами'
        },
        'classes': {
            'title': 'Классы',
            'icon': '🏗️',
            'color': '#10B981',
            'description': 'ООП и классы в JavaScript'
        },
        'matrices': {
            'title': 'Матрицы',
            'icon': '🔢',
            'color': '#EF4444',
            'description': 'Двумерные массивы и матрицы'
        }
    }
    
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
        md_topics = {
            'closures': {
                'title': 'Замыкания',
                'icon': '🔒',
                'color': '#8B5CF6',
                'description': 'Функции и области видимости'
            },
            'throttle_debounce': {
                'title': 'Тротлы и дебаунсы',
                'icon': '⏱️',
                'color': '#F97316',
                'description': 'Оптимизация производительности'
            },
            'custom_functions': {
                'title': 'Кастомные методы и функции',
                'icon': '⚡',
                'color': '#3B82F6',
                'description': 'Создание собственных функций и методов'
            },
            'time': {
                'title': 'Часовая',
                'icon': '🕐',
                'color': '#06B6D4',
                'description': 'Работа с временем и датами'
            },
            'arrays': {
                'title': 'Массивы',
                'icon': '📝',
                'color': '#F59E0B',
                'description': 'Работа с массивами и их методами'
            },
            'promises': {
                'title': 'Промисы',
                'icon': '🔄',
                'color': '#06B6D4',
                'description': 'Асинхронная работа и промисы'
            },
            'strings': {
                'title': 'Строки',
                'icon': '🔤',
                'color': '#8B5CF6',
                'description': 'Обработка строк и регулярные выражения'
            },
            'objects': {
                'title': 'Объекты',
                'icon': '📦',
                'color': '#84CC16',
                'description': 'Работа с объектами и их свойствами'
            },
            'classes': {
                'title': 'Классы',
                'icon': '🏗️',
                'color': '#10B981',
                'description': 'ООП и классы в JavaScript'
            },
            'matrices': {
                'title': 'Матрицы',
                'icon': '🔢',
                'color': '#EF4444',
                'description': 'Двумерные массивы и матрицы'
            }
        }
        
        if topic_key not in md_topics:
            raise HTTPException(status_code=404, detail=f"Группа '{topic_key}' не найдена")
        
        topic_config = md_topics[topic_key]
        
        mock_tasks = [
            {
                'id': f'task_{topic_key}_1',
                'title': f'Пример задачи 1 - {topic_config["title"]}',
                'description': f'Это пример задачи для группы {topic_config["title"]}',
                'complexity_score': 3.5,
                'target_skill_level': 'intermediate',
                'estimated_time_minutes': 30,
                'programming_concepts': [topic_key],
                'js_features_used': ['functions', 'variables']
            },
            {
                'id': f'task_{topic_key}_2',
                'title': f'Пример задачи 2 - {topic_config["title"]}',
                'description': f'Еще одна пример задачи для группы {topic_config["title"]}',
                'complexity_score': 5.0,
                'target_skill_level': 'advanced',
                'estimated_time_minutes': 45,
                'programming_concepts': [topic_key],
                'js_features_used': ['functions', 'objects']
            }
        ]
        
        return {
            "success": True,
            "topic": {
                "key": topic_key,
                "title": topic_config['title'],
                "icon": topic_config['icon'],
                "color": topic_config['color'],
                "description": topic_config['description']
            },
            "tasks": mock_tasks,
            "total_tasks": len(mock_tasks),
            "applied_filters": {
                "difficulty": difficulty_filter
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения задач: {str(e)}") 