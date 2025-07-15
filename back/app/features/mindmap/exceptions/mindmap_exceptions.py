"""Исключения для работы с ментальными картами"""

from app.core.exceptions import BaseApplicationException, NotFoundException


class MindMapError(BaseApplicationException):
    """Базовое исключение для работы с mindmap"""
    
    def __init__(self, message: str = "Ошибка при работе с ментальной картой", details: str = None):
        from app.core.exceptions import ErrorCode
        super().__init__(message, ErrorCode.INTERNAL_ERROR, details, 500)


class TechnologyNotSupportedError(MindMapError):
    """Исключение при неподдерживаемой технологии"""
    
    def __init__(self, technology: str):
        super().__init__(f"Технология '{technology}' не поддерживается")


class TopicNotFoundError(NotFoundException):
    """Исключение при отсутствии топика"""
    
    def __init__(self, topic_key: str, technology: str = None):
        tech_info = f" для технологии '{technology}'" if technology else ""
        super().__init__(f"Топик '{topic_key}'{tech_info}")


class TaskNotFoundError(NotFoundException):
    """Исключение при отсутствии задачи"""
    
    def __init__(self, task_id: str):
        super().__init__(f"Задача с ID '{task_id}'") 


