from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
import logging
from datetime import datetime

from ..database import get_db
from ..models import ContentBlock, UserContentProgress
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from deep_content_analysis import DeepContentAnalyzer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/mindmap", tags=["mindmap"])

@router.get("/generate")
async def generate_mindmap(
    db: Session = Depends(get_db),
    structure_type: str = "topics",  # "topics" или "legacy"
    difficulty_filter: Optional[str] = None,  # "beginner", "intermediate", "advanced"
    concept_filter: Optional[str] = None,      # "arrays", "functions", etc.
    topic_filter: Optional[str] = None         # "closures", "arrays", etc.
) -> Dict[str, Any]:
    """
    Генерирует данные для MindMap на основе анализа задач
    """
    try:
        logger.info(f"🎯 Генерация mindmap (структура: {structure_type}, фильтры: difficulty={difficulty_filter}, topic={topic_filter})")
        
        # Используем наш детальный анализатор
        analyzer = DeepContentAnalyzer()
        
        # Загружаем готовый анализ если есть
        try:
            with open("detailed_analysis_result.json", "r", encoding="utf-8") as f:
                analysis_data = json.load(f)
        except FileNotFoundError:
            # Если файла нет, делаем анализ заново
            logger.info("📊 Создаем новый анализ задач...")
            analysis_result = analyzer.analyze_all_tasks()
            analysis_data = {
                'task_analyses': [analysis.__dict__ for analysis in analysis_result['task_analyses']],
                'concept_clusters': analysis_result['concept_clusters'],
                'learning_sequences': analysis_result['learning_sequences'],
                'path_structure': analysis_result['path_structure'],
                'summary_stats': analysis_result['summary_stats'],
                'topic_structure': analysis_result['topic_structure']  # Новое поле
            }
            
            # Сохраняем результат
            with open("detailed_analysis_result.json", "w", encoding="utf-8") as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2, default=str)
            logger.info("💾 Анализ сохранен в detailed_analysis_result.json")
        
        # Генерируем данные для React Flow в зависимости от типа структуры
        if structure_type == "topics":
            logger.info("🎨 Генерируем новую структуру по темам...")
            mindmap_data = generate_topic_based_mindmap(
                analysis_data,
                difficulty_filter=difficulty_filter,
                topic_filter=topic_filter
            )
        else:
            logger.info("🔄 Генерируем старую структуру...")
            mindmap_data = generate_react_flow_data(
                analysis_data, 
                difficulty_filter=difficulty_filter,
                concept_filter=concept_filter
            )
        
        logger.info(f"✅ Mindmap сгенерирована: {mindmap_data['total_nodes']} узлов, {mindmap_data['total_edges']} связей")
        
        return {
            "success": True,
            "data": mindmap_data,
            "structure_type": structure_type,
            "metadata": {
                "total_tasks": analysis_data.get('summary_stats', {}).get('total_tasks', 0),
                "generated_at": datetime.now().isoformat(),
                "filters_applied": {
                    "difficulty": difficulty_filter,
                    "concept": concept_filter,
                    "topic": topic_filter
                }
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка генерации mindmap: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка генерации mindmap: {str(e)}")

def generate_react_flow_data(
    analysis_data: Dict[str, Any], 
    difficulty_filter: Optional[str] = None,
    concept_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Преобразует данные анализа в формат React Flow
    """
    tasks = analysis_data['task_analyses']
    clusters = analysis_data['concept_clusters']
    sequences = analysis_data['learning_sequences']
    
    # Фильтруем задачи если нужно
    filtered_tasks = tasks
    if difficulty_filter:
        filtered_tasks = [t for t in filtered_tasks if t.get('target_skill_level') == difficulty_filter]
    if concept_filter:
        filtered_tasks = [t for t in filtered_tasks if concept_filter in t.get('programming_concepts', [])]
    
    nodes = []
    edges = []
    
    # 1. Создаем центральный узел
    nodes.append({
        "id": "center",
        "type": "centerNode",
        "position": {"x": 400, "y": 300},
        "data": {
            "label": "JavaScript Learning Path",
            "description": f"Интерактивная карта изучения ({len(filtered_tasks)} задач)",
            "type": "center"
        }
    })
    
    # 2. Создаем узлы концепций (основные ветки)
    main_concepts = ['functions', 'arrays', 'objects', 'strings', 'classes', 'async']
    concept_positions = [
        {"x": 100, "y": 100},   # functions
        {"x": 700, "y": 100},   # arrays  
        {"x": 700, "y": 500},   # objects
        {"x": 100, "y": 500},   # strings
        {"x": 200, "y": 50},    # classes
        {"x": 600, "y": 50},    # async
    ]
    
    for i, concept in enumerate(main_concepts):
        if concept in clusters:
            concept_tasks = [t for t in filtered_tasks if t['id'] in clusters[concept]]
            if concept_tasks:
                # Вычисляем статистику концепции
                avg_complexity = sum(t['complexity_score'] for t in concept_tasks) / len(concept_tasks)
                difficulty_color = get_difficulty_color(avg_complexity)
                
                nodes.append({
                    "id": f"concept_{concept}",
                    "type": "conceptNode", 
                    "position": concept_positions[i],
                    "data": {
                        "label": concept.title(),
                        "task_count": len(concept_tasks),
                        "avg_complexity": round(avg_complexity, 1),
                        "difficulty_color": difficulty_color,
                        "concept": concept,
                        "type": "concept"
                    }
                })
                
                # Связь с центром
                edges.append({
                    "id": f"edge_center_{concept}",
                    "source": "center",
                    "target": f"concept_{concept}",
                    "type": "conceptEdge",
                    "animated": True
                })
    
    # 3. Создаем узлы путей обучения (pathTitles)
    path_clusters = {k: v for k, v in clusters.items() if k.startswith('path_')}
    path_y_offset = 200
    
    for i, (path_name, task_ids) in enumerate(path_clusters.items()):
        path_tasks = [t for t in filtered_tasks if t['id'] in task_ids]
        if path_tasks and len(path_tasks) >= 3:  # Показываем только значимые пути
            
            clean_path_name = path_name.replace('path_', '').replace('_', ' ')
            avg_complexity = sum(t['complexity_score'] for t in path_tasks) / len(path_tasks)
            
            nodes.append({
                "id": f"path_{i}",
                "type": "pathNode",
                "position": {"x": 200 + i * 150, "y": path_y_offset + i * 80},
                "data": {
                    "label": clean_path_name[:30] + "..." if len(clean_path_name) > 30 else clean_path_name,
                    "full_title": clean_path_name,
                    "task_count": len(path_tasks),
                    "avg_complexity": round(avg_complexity, 1),
                    "difficulty_color": get_difficulty_color(avg_complexity),
                    "type": "path"
                }
            })
            
            # Связь с центром  
            edges.append({
                "id": f"edge_center_path_{i}",
                "source": "center", 
                "target": f"path_{i}",
                "type": "pathEdge"
            })
    
    # 4. Создаем узлы сложности
    difficulty_levels = ['beginner', 'intermediate', 'advanced']
    difficulty_positions = [
        {"x": 50, "y": 300},   # beginner
        {"x": 400, "y": 150},  # intermediate  
        {"x": 750, "y": 300},  # advanced
    ]
    
    for i, level in enumerate(difficulty_levels):
        level_tasks = [t for t in filtered_tasks if t.get('target_skill_level') == level]
        if level_tasks:
            nodes.append({
                "id": f"difficulty_{level}",
                "type": "difficultyNode",
                "position": difficulty_positions[i],
                "data": {
                    "label": level.title(),
                    "task_count": len(level_tasks),
                    "percentage": round(len(level_tasks) / len(filtered_tasks) * 100, 1),
                    "difficulty_color": get_difficulty_color_by_level(level),
                    "type": "difficulty"
                }
            })
            
            # Связь с центром
            edges.append({
                "id": f"edge_center_{level}",
                "source": "center",
                "target": f"difficulty_{level}",
                "type": "difficultyEdge"
            })
    
    # 5. Добавляем связи между концепциями (prerequisites)
    concept_prerequisites = {
        'arrays': ['functions'],
        'objects': ['functions'], 
        'classes': ['objects', 'functions'],
        'async': ['functions', 'objects']
    }
    
    for concept, prereqs in concept_prerequisites.items():
        if f"concept_{concept}" in [n['id'] for n in nodes]:
            for prereq in prereqs:
                if f"concept_{prereq}" in [n['id'] for n in nodes]:
                    edges.append({
                        "id": f"prereq_{prereq}_{concept}",
                        "source": f"concept_{prereq}",
                        "target": f"concept_{concept}",
                        "type": "prerequisiteEdge",
                        "animated": False,
                        "style": {"strokeDasharray": "5,5"}
                    })
    
    return {
        "nodes": nodes,
        "edges": edges,
        "layout": "hierarchy",
        "total_nodes": len(nodes),
        "total_edges": len(edges)
    }

def generate_topic_based_mindmap(
    analysis_data: Dict[str, Any],
    difficulty_filter: Optional[str] = None,
    topic_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Генерирует ПРОСТОЙ mind map: центр -> темы -> 3-4 задачи
    """
    logger.info("🎨 Создаем ПРОСТОЙ майндмап: только темы и задачи...")
    
    md_topics = {
        'closures': {
            'title': 'Замыкания',
            'icon': '🔒',
            'color': '#8B5CF6',
            'description': 'Функции и области видимости',
            'keywords': ['closure', 'замыка', 'замыкание', 'scope', 'lexical', 'inner function', 'outer function']
        },
        'custom_functions': {
            'title': 'Кастомные методы и функции',
            'icon': '⚡',
            'color': '#3B82F6',
            'description': 'Создание собственных функций и методов',
            'keywords': ['sum', 'compose', 'pipe', 'memo', 'memoization', 'once', 'throttle', 'debounce', 'map', 'filter', 'reduce', 'forEach', 'implement']
        },
        'classes': {
            'title': 'Классы',
            'icon': '🏗️',
            'color': '#10B981',
            'description': 'ООП и классы в JavaScript',
            'keywords': ['class', 'constructor', 'класс', 'singleton', 'store', 'extends', 'inheritance', 'prototype', 'this', 'new']
        },
        'arrays': {
            'title': 'Массивы',
            'icon': '📝',
            'color': '#F59E0B',
            'description': 'Работа с массивами и их методами',
            'keywords': ['array', 'массив', 'findminmax', 'chunk', 'twosum', 'groupanagrams', 'duplicate', 'sort', 'push', 'pop', 'splice', 'slice']
        },
        'matrices': {
            'title': 'Матрицы',
            'icon': '🔢',
            'color': '#EF4444',
            'description': 'Двумерные массивы и матрицы',
            'keywords': ['matrix', 'матрица', 'grid', 'двумерный', 'battleships', 'rotate', 'spiral', '2d array', 'table']
        },
        'objects': {
            'title': 'Объекты',
            'icon': '📦',
            'color': '#84CC16',
            'description': 'Работа с объектами и их свойствами',
            'keywords': ['object', 'объект', 'property', 'свойство', 'collectvalues', 'dfs', 'bfs', 'tree', 'keys', 'values', 'entries']
        },
        'promises': {
            'title': 'Промисы',
            'icon': '🔄',
            'color': '#06B6D4',
            'description': 'Асинхронная работа и промисы',
            'keywords': ['promise', 'async', 'await', 'промис', 'sleep', 'timelimit', 'promisify', 'withretry', 'then', 'catch', 'finally']
        },
        'strings': {
            'title': 'Строки',
            'icon': '🔤',
            'color': '#8B5CF6',
            'description': 'Обработка строк и регулярные выражения',
            'keywords': ['string', 'строка', 'text', 'текст', 'anagram', 'palindrome', 'compress', 'reverse', 'charAt', 'substring', 'split', 'join']
        },
        'throttle_debounce': {
            'title': 'Тротлы и дебаунсы',
            'icon': '⏱️',
            'color': '#F97316',
            'description': 'Оптимизация производительности',
            'keywords': ['throttle', 'debounce', 'тротл', 'дебаунс', 'limit', 'delay', 'timeout']
        },
        'numbers': {
            'title': 'Числа',
            'icon': '🔢',
            'color': '#EC4899',
            'description': 'Математические операции и числа',
            'keywords': ['number', 'число', 'math', 'математика', 'factorial', 'fibonacci', 'fizzbuzz', 'prime', 'sum', 'multiply', 'divide']
        }
    }
    
    tasks = analysis_data.get('task_analyses', [])
    
    topic_tasks = {}
    used_task_ids = set()
    
    technical_titles_to_exclude = [
        'тип функции', 'тип параметров', 'исключение свойства', 'выбор свойств',
        'необязательные свойства', 'обязательные свойства', 'исключение z',
        'опциональные свойства', 'тип возвращаемого значения'
    ]
    
    # Исключаем конкретные проблемные задачи
    problematic_task_ids = [
        'cmbhuxzkv005dhxt8tktsk6gn',  # Функция-замыкание с авто...
        'cmbhuy1x6006phxt8or6px97n'   # Ответ:
    ]
    
    for task in tasks:
        task_id = task.get('id')
        if task_id in used_task_ids:
            continue
        
        if task_id in problematic_task_ids:
            continue
        
        task_title = task.get('title', '').lower()
        
        # Исключаем задачи по содержанию заголовка
        if (task_title.startswith('функция-замыкание') or 
            task_title.startswith('ответ:') or
            'функция-замыкание с авто' in task_title):
            continue
        
        if any(tech_title in task_title for tech_title in technical_titles_to_exclude):
            continue
            
        task_content = (task.get('title', '') + ' ' + 
                       task.get('text_content', '') + ' ' + 
                       task.get('code_content', '') + ' ' +
                       ' '.join(task.get('keywords', []))).lower()
        
        for topic_key, topic_config in md_topics.items():
            if any(keyword in task_content for keyword in topic_config['keywords']):
                if topic_key not in topic_tasks:
                    topic_tasks[topic_key] = []
                topic_tasks[topic_key].append(task)
                used_task_ids.add(task_id)
                break
    
    logger.info(f"📊 Распределение задач БЕЗ ДУБЛИРОВАНИЯ:")
    for topic_key, tasks_list in topic_tasks.items():
        logger.info(f"   📌 {md_topics[topic_key]['title']}: {len(tasks_list)} задач")
    
    nodes = []
    edges = []
    
    total_assigned_tasks = sum(len(tasks_list) for tasks_list in topic_tasks.values())
    
    nodes.append({
        "id": "center",
        "type": "center",
        "position": {"x": 500, "y": 400},
        "data": {
            "title": "JavaScript Skills",
            "description": f"Изучение JavaScript ({total_assigned_tasks} задач)",
            "total_tasks": total_assigned_tasks,
            "type": "center"
        }
    })
    
    import math
    radius = 400
    
    active_topics = [(topic_key, topic_config, tasks_list) 
                    for topic_key, topic_config in md_topics.items() 
                    if topic_key in topic_tasks and len(topic_tasks[topic_key]) > 0]
    
    if topic_filter:
        active_topics = [(k, c, t) for k, c, t in active_topics if k == topic_filter]
    
    topic_count = len(active_topics)
    logger.info(f"🎯 Отображаем {topic_count} активных тем")
    
    for i, (topic_key, topic_config, tasks_list) in enumerate(active_topics):
        angle = (2 * math.pi * i) / topic_count
        x = 500 + radius * math.cos(angle)
        y = 400 + radius * math.sin(angle)
        
        filtered_tasks = tasks_list
        if difficulty_filter:
            filtered_tasks = [t for t in tasks_list if t.get('target_skill_level') == difficulty_filter]
        
        if not filtered_tasks:
            continue
        
        nodes.append({
            "id": f"topic_{topic_key}",
            "type": "topic",
            "position": {"x": x, "y": y},
            "data": {
                "title": topic_config['title'],
                "icon": topic_config['icon'],
                "color": topic_config['color'],
                "description": topic_config['description'],
                "task_count": len(filtered_tasks),
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
        
        max_tasks_to_show = 3
        tasks_to_show = filtered_tasks[:max_tasks_to_show]
        task_radius = 120
        
        for j, task in enumerate(tasks_to_show):
            task_angle = angle + (2 * math.pi * j) / 3 - math.pi/2
            task_x = x + task_radius * math.cos(task_angle)
            task_y = y + task_radius * math.sin(task_angle)
            
            task_title = task.get('title', 'Задача без названия')
            if task_title.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                task_title = task_title.split('.', 1)[1].strip()
            
            display_title = task_title[:25] + "..." if len(task_title) > 25 else task_title
            
            nodes.append({
                "id": f"task_{task.get('id')}",
                "type": "task",
                "position": {"x": task_x, "y": task_y},
                "data": {
                    "title": display_title,
                    "full_title": task_title,
                    "task_id": task.get('id'),
                    "parent_topic": topic_key,
                    "color": topic_config['color'],
                    "type": "task"
                }
            })
            
            edges.append({
                "id": f"edge_{topic_key}_task_{task.get('id')}",
                "source": f"topic_{topic_key}",
                "target": f"task_{task.get('id')}",
                "style": {
                    "stroke": topic_config['color'],
                    "strokeWidth": 1,
                    "strokeOpacity": 0.7
                }
            })
    
    logger.info(f"✅ ПРОСТОЙ майндмап создан: {len(nodes)} узлов, {len(edges)} связей")
    
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

def get_difficulty_color(complexity: float) -> str:
    """Возвращает цвет на основе сложности"""
    if complexity <= 1.0:
        return "#10B981"  # green (easy)
    elif complexity <= 2.5:
        return "#F59E0B"  # yellow (medium)
    elif complexity <= 5.0:
        return "#EF4444"  # red (hard)
    else:
        return "#8B5CF6"  # purple (expert)

def get_difficulty_color_by_level(level: str) -> str:
    """Возвращает цвет на основе уровня"""
    colors = {
        "beginner": "#10B981",
        "intermediate": "#F59E0B", 
        "advanced": "#EF4444"
    }
    return colors.get(level, "#6B7280")

@router.get("/task/{task_id}")
async def get_task_details(task_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Получает детальную информацию о задаче для popup
    """
    try:
        # Загружаем анализ
        with open("detailed_analysis_result.json", "r", encoding="utf-8") as f:
            analysis_data = json.load(f)
        
        # Находим задачу
        task = next((t for t in analysis_data['task_analyses'] if t['id'] == task_id), None)
        if not task:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        
        # Получаем связанные задачи
        related_tasks = []
        task_connections = analysis_data.get('task_connections', {})
        if task_id in task_connections:
            related_ids = task_connections[task_id][:3]  # топ-3 связанных
            related_tasks = [
                t for t in analysis_data['task_analyses'] 
                if t['id'] in related_ids
            ]
        
        return {
            "success": True,
            "task": task,
            "related_tasks": [
                {
                    "id": rt['id'],
                    "title": rt['title'],
                    "complexity_score": rt['complexity_score'],
                    "target_skill_level": rt['target_skill_level']
                }
                for rt in related_tasks
            ]
        }
        
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Анализ данных не найден. Запустите генерацию mindmap сначала.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения задачи: {str(e)}") 