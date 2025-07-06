"""Admin domain entities."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class SystemStats:
    """Общая статистика системы"""
    users: Dict[str, int]
    content: Dict[str, int]
    progress: Dict[str, int]


@dataclass
class UserStats:
    """Статистика пользователя"""
    id: str
    email: str
    role: str
    created_at: datetime
    updated_at: datetime
    content_progress_count: int
    theory_progress_count: int


@dataclass
class ContentStats:
    """Статистика контента"""
    total_files: int
    total_blocks: int
    files_by_category: Dict[str, int]
    blocks_by_category: Dict[str, int]


@dataclass
class TheoryStats:
    """Статистика теории"""
    total_cards: int
    cards_by_category: Dict[str, int]
    cards_by_type: Dict[str, int]


@dataclass
class AdminContentFile:
    """Файл контента для админки"""
    id: str
    webdav_path: str
    main_category: str
    sub_category: str
    created_at: datetime
    updated_at: datetime
    blocks_count: int


@dataclass
class AdminContentBlock:
    """Блок контента для админки"""
    id: str
    file_id: str
    path_titles: List[str]
    block_title: str
    block_level: int
    order_in_file: int
    text_content: Optional[str]
    code_content: Optional[str]
    code_language: Optional[str]
    is_code_foldable: bool
    code_fold_title: Optional[str]
    extracted_urls: List[str]
    created_at: datetime
    updated_at: datetime


@dataclass
class AdminTheoryCard:
    """Карточка теории для админки"""
    id: str
    anki_guid: Optional[str]
    card_type: str
    deck: str
    category: str
    sub_category: Optional[str]
    question_block: str
    answer_block: str
    tags: List[str]
    order_index: int
    created_at: datetime
    updated_at: datetime


@dataclass
class AdminUser:
    """Пользователь для админки"""
    id: str
    email: str
    role: str
    created_at: datetime
    updated_at: datetime
    content_progress_count: int = 0
    theory_progress_count: int = 0


@dataclass
class BulkDeleteResult:
    """Результат массового удаления"""
    deleted_count: int
    failed_ids: List[str] = field(default_factory=list)
    error_messages: List[str] = field(default_factory=list) 