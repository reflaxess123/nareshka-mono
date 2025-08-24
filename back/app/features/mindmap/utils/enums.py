"""Enums для mindmap модуля"""

from enum import Enum


class ProgressStatus(str, Enum):
    """Статусы прогресса задач"""
    
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"


class MindMapStructureType(str, Enum):
    """Типы структур mindmap"""
    
    TOPICS = "topics"


class MindMapLayout(str, Enum):
    """Типы макетов mindmap"""
    
    RADIAL = "radial"


class NodeType(str, Enum):
    """Типы узлов mindmap"""
    
    CENTER = "center"
    TOPIC = "topic"


class Technology(str, Enum):
    """Поддерживаемые технологии"""
    
    JAVASCRIPT = "javascript"
    REACT = "react"
    TYPESCRIPT = "typescript"
    INTERVIEWS = "interviews"


class CodeLanguage(str, Enum):
    """Языки программирования"""
    
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    PYTHON = "python"