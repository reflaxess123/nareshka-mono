"""Admin repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..entities.admin import (
    SystemStats, UserStats, ContentStats, TheoryStats,
    AdminContentFile, AdminContentBlock, AdminTheoryCard,
    AdminUser, BulkDeleteResult
)


class AdminRepository(ABC):
    """Интерфейс репозитория для административных операций"""
    
    @abstractmethod
    async def get_system_stats(self) -> SystemStats:
        """Получить общую статистику системы"""
        pass
    
    @abstractmethod
    async def get_users_with_stats(
        self, 
        skip: int = 0, 
        limit: int = 20,
        role: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[UserStats], int]:
        """Получить пользователей с подсчетом прогресса"""
        pass
    
    @abstractmethod
    async def create_user(self, email: str, password_hash: str, role: str) -> AdminUser:
        """Создать нового пользователя"""
        pass
    
    @abstractmethod
    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> Optional[AdminUser]:
        """Обновить пользователя"""
        pass
    
    @abstractmethod
    async def delete_user(self, user_id: str) -> bool:
        """Удалить пользователя"""
        pass
    
    @abstractmethod
    async def get_content_stats(self) -> ContentStats:
        """Получить статистику контента"""
        pass
    
    @abstractmethod
    async def get_content_files(
        self,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[AdminContentFile], int]:
        """Получить файлы контента"""
        pass
    
    @abstractmethod
    async def create_content_file(
        self,
        webdav_path: str,
        main_category: str,
        sub_category: str
    ) -> AdminContentFile:
        """Создать файл контента"""
        pass
    
    @abstractmethod
    async def update_content_file(
        self,
        file_id: str,
        updates: Dict[str, Any]
    ) -> Optional[AdminContentFile]:
        """Обновить файл контента"""
        pass
    
    @abstractmethod
    async def delete_content_file(self, file_id: str) -> bool:
        """Удалить файл контента"""
        pass
    
    @abstractmethod
    async def get_content_blocks(
        self,
        skip: int = 0,
        limit: int = 20,
        file_id: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[AdminContentBlock], int]:
        """Получить блоки контента"""
        pass
    
    @abstractmethod
    async def create_content_block(
        self,
        file_id: str,
        path_titles: List[str],
        block_title: str,
        block_level: int,
        order_in_file: int,
        text_content: Optional[str] = None,
        code_content: Optional[str] = None,
        code_language: Optional[str] = None,
        is_code_foldable: bool = False,
        code_fold_title: Optional[str] = None,
        extracted_urls: List[str] = None
    ) -> AdminContentBlock:
        """Создать блок контента"""
        pass
    
    @abstractmethod
    async def update_content_block(
        self,
        block_id: str,
        updates: Dict[str, Any]
    ) -> Optional[AdminContentBlock]:
        """Обновить блок контента"""
        pass
    
    @abstractmethod
    async def delete_content_block(self, block_id: str) -> bool:
        """Удалить блок контента"""
        pass
    
    @abstractmethod
    async def get_theory_cards(
        self,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[AdminTheoryCard], int]:
        """Получить карточки теории"""
        pass
    
    @abstractmethod
    async def create_theory_card(
        self,
        anki_guid: Optional[str],
        card_type: str,
        deck: str,
        category: str,
        sub_category: Optional[str],
        question_block: str,
        answer_block: str,
        tags: List[str],
        order_index: int
    ) -> AdminTheoryCard:
        """Создать карточку теории"""
        pass
    
    @abstractmethod
    async def update_theory_card(
        self,
        card_id: str,
        updates: Dict[str, Any]
    ) -> Optional[AdminTheoryCard]:
        """Обновить карточку теории"""
        pass
    
    @abstractmethod
    async def delete_theory_card(self, card_id: str) -> bool:
        """Удалить карточку теории"""
        pass
    
    @abstractmethod
    async def bulk_delete_content(self, ids: List[str]) -> BulkDeleteResult:
        """Массово удалить контент"""
        pass
    
    @abstractmethod
    async def bulk_delete_theory(self, ids: List[str]) -> BulkDeleteResult:
        """Массово удалить теорию"""
        pass 