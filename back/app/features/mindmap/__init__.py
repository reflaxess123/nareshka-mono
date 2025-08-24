"""
MindMap Feature

Модуль для работы с ментальными картами:
- Генерация mindmap структур для технологий
- Визуализация прогресса пользователя
- Топики и задачи с интерактивным отображением
- Интеграция с контентом и прогрессом пользователя
"""

# Router импортируется напрямую в main.py для избежания циклических импортов
from app.features.mindmap.repositories.mindmap_repository import MindMapRepository
from app.features.mindmap.services.mindmap_service import MindMapService

__all__ = [
    "MindMapService",
    "MindMapRepository",
]
