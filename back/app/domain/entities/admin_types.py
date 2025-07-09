"""Admin types для внутреннего использования в services и repositories."""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel


class SystemStats(BaseModel):
    """Статистика системы"""
    users: Dict[str, int]
    content: Dict[str, int]
    progress: Dict[str, int]


class UserStats(BaseModel):
    """Статистика пользователя"""
    id: int
    email: str
    role: str
    created_at: datetime
    updated_at: datetime
    content_progress_count: int
    theory_progress_count: int


class ContentStats(BaseModel):
    """Статистика контента"""
    total_files: int
    total_blocks: int
    files_by_category: Dict[str, int]
    blocks_by_category: Dict[str, int]


class TheoryStats(BaseModel):
    """Статистика теории"""
    total_cards: int
    cards_by_category: Dict[str, int]
    cards_by_deck: Dict[str, int]


class AdminUser(BaseModel):
    """Admin представление пользователя"""
    id: int
    email: str
    role: str
    created_at: datetime
    updated_at: datetime


class AdminContentFile(BaseModel):
    """Admin представление файла контента"""
    id: str
    webdav_path: str
    main_category: str
    sub_category: str
    created_at: datetime
    updated_at: datetime
    blocks_count: int = 0


class AdminContentBlock(BaseModel):
    """Admin представление блока контента"""
    id: str
    file_id: str
    path_titles: List[str]
    block_title: str
    block_level: int
    order_in_file: int
    text_content: Optional[str] = None
    code_content: Optional[str] = None
    code_language: Optional[str] = None
    is_code_foldable: bool = False
    code_fold_title: Optional[str] = None
    extracted_urls: List[str] = []
    created_at: datetime
    updated_at: datetime


class AdminTheoryCard(BaseModel):
    """Admin представление карточки теории"""
    id: str
    anki_guid: Optional[str] = None
    card_type: str
    deck: str
    category: str
    sub_category: Optional[str] = None
    question_block: str
    answer_block: str
    tags: List[str] = []
    order_index: int = 0
    created_at: datetime
    updated_at: datetime


class BulkDeleteResult(BaseModel):
    """Результат массового удаления"""
    deleted_count: int
    error_count: int
    errors: List[str] = [] 