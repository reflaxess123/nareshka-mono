"""Task types для внутреннего использования в services и repositories."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from ..entities.enums import CodeLanguage


class TaskType(BaseModel):
    """Тип задачи"""
    name: str
    display_name: str
    description: Optional[str] = None


class TaskCategory(BaseModel):
    """Категория задач"""
    main_category: str
    sub_category: Optional[str] = None
    task_count: int = 0


class TaskCompany(BaseModel):
    """Компания из задач"""
    company: str
    task_count: int = 0


class Task(BaseModel):
    """Задача/задание"""
    id: str
    title: str
    description: Optional[str] = None
    main_category: str
    sub_category: Optional[str] = None
    item_type: str  # 'content_block' или 'theory_quiz'
    difficulty: Optional[str] = None
    companies: List[str] = []
    tags: List[str] = []
    code_content: Optional[str] = None
    code_language: Optional[CodeLanguage] = None
    is_solved: bool = False
    progress_percentage: float = 0.0
    order_in_file: int = 0
    created_at: datetime
    updated_at: datetime 