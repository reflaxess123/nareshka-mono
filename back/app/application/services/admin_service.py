"""Admin service for business logic."""

from typing import List, Optional, Dict, Any
from ...domain.repositories.admin_repository import AdminRepository
from ...domain.entities.admin import (
    SystemStats, UserStats, ContentStats, TheoryStats,
    AdminContentFile, AdminContentBlock, AdminTheoryCard,
    AdminUser, BulkDeleteResult
)
from ...application.services.auth_service import AuthService


class AdminService:
    """Сервис для административных операций"""
    
    def __init__(self, admin_repository: AdminRepository, auth_service: AuthService):
        self.admin_repository = admin_repository
        self.auth_service = auth_service
    
    async def get_system_stats(self) -> SystemStats:
        """Получить общую статистику системы"""
        return await self.admin_repository.get_system_stats()
    
    async def get_users_with_stats(
        self, 
        skip: int = 0, 
        limit: int = 20,
        role: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[UserStats], int]:
        """Получить пользователей с подсчетом прогресса"""
        return await self.admin_repository.get_users_with_stats(
            skip=skip, 
            limit=limit, 
            role=role, 
            search=search
        )
    
    async def create_user(
        self, 
        email: str, 
        password: str, 
        role: str = "USER"
    ) -> AdminUser:
        """Создать нового пользователя"""
        # Хешируем пароль
        password_hash = self.auth_service.get_password_hash(password)
        
        return await self.admin_repository.create_user(
            email=email,
            password_hash=password_hash,
            role=role
        )
    
    async def update_user(
        self, 
        user_id: str, 
        email: Optional[str] = None,
        password: Optional[str] = None,
        role: Optional[str] = None
    ) -> Optional[AdminUser]:
        """Обновить пользователя"""
        updates = {}
        
        if email is not None:
            updates["email"] = email
        
        if password is not None:
            updates["password_hash"] = self.auth_service.get_password_hash(password)
        
        if role is not None:
            updates["role"] = role
        
        return await self.admin_repository.update_user(user_id, updates)
    
    async def delete_user(self, user_id: str) -> bool:
        """Удалить пользователя"""
        return await self.admin_repository.delete_user(user_id)
    
    async def get_content_stats(self) -> ContentStats:
        """Получить статистику контента"""
        return await self.admin_repository.get_content_stats()
    
    async def get_content_files(
        self,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[AdminContentFile], int]:
        """Получить файлы контента"""
        return await self.admin_repository.get_content_files(
            skip=skip,
            limit=limit,
            category=category,
            search=search
        )
    
    async def create_content_file(
        self,
        webdav_path: str,
        main_category: str,
        sub_category: str
    ) -> AdminContentFile:
        """Создать файл контента"""
        return await self.admin_repository.create_content_file(
            webdav_path=webdav_path,
            main_category=main_category,
            sub_category=sub_category
        )
    
    async def update_content_file(
        self,
        file_id: str,
        webdav_path: Optional[str] = None,
        main_category: Optional[str] = None,
        sub_category: Optional[str] = None
    ) -> Optional[AdminContentFile]:
        """Обновить файл контента"""
        updates = {}
        
        if webdav_path is not None:
            updates["webdav_path"] = webdav_path
        
        if main_category is not None:
            updates["main_category"] = main_category
        
        if sub_category is not None:
            updates["sub_category"] = sub_category
        
        return await self.admin_repository.update_content_file(file_id, updates)
    
    async def delete_content_file(self, file_id: str) -> bool:
        """Удалить файл контента"""
        return await self.admin_repository.delete_content_file(file_id)
    
    async def get_content_blocks(
        self,
        skip: int = 0,
        limit: int = 20,
        file_id: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[AdminContentBlock], int]:
        """Получить блоки контента"""
        return await self.admin_repository.get_content_blocks(
            skip=skip,
            limit=limit,
            file_id=file_id,
            search=search
        )
    
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
        return await self.admin_repository.create_content_block(
            file_id=file_id,
            path_titles=path_titles,
            block_title=block_title,
            block_level=block_level,
            order_in_file=order_in_file,
            text_content=text_content,
            code_content=code_content,
            code_language=code_language,
            is_code_foldable=is_code_foldable,
            code_fold_title=code_fold_title,
            extracted_urls=extracted_urls or []
        )
    
    async def update_content_block(
        self,
        block_id: str,
        file_id: Optional[str] = None,
        path_titles: Optional[List[str]] = None,
        block_title: Optional[str] = None,
        block_level: Optional[int] = None,
        order_in_file: Optional[int] = None,
        text_content: Optional[str] = None,
        code_content: Optional[str] = None,
        code_language: Optional[str] = None,
        is_code_foldable: Optional[bool] = None,
        code_fold_title: Optional[str] = None,
        extracted_urls: Optional[List[str]] = None
    ) -> Optional[AdminContentBlock]:
        """Обновить блок контента"""
        updates = {}
        
        if file_id is not None:
            updates["file_id"] = file_id
        if path_titles is not None:
            updates["path_titles"] = path_titles
        if block_title is not None:
            updates["block_title"] = block_title
        if block_level is not None:
            updates["block_level"] = block_level
        if order_in_file is not None:
            updates["order_in_file"] = order_in_file
        if text_content is not None:
            updates["text_content"] = text_content
        if code_content is not None:
            updates["code_content"] = code_content
        if code_language is not None:
            updates["code_language"] = code_language
        if is_code_foldable is not None:
            updates["is_code_foldable"] = is_code_foldable
        if code_fold_title is not None:
            updates["code_fold_title"] = code_fold_title
        if extracted_urls is not None:
            updates["extracted_urls"] = extracted_urls
        
        return await self.admin_repository.update_content_block(block_id, updates)
    
    async def delete_content_block(self, block_id: str) -> bool:
        """Удалить блок контента"""
        return await self.admin_repository.delete_content_block(block_id)
    
    async def get_theory_cards(
        self,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[AdminTheoryCard], int]:
        """Получить карточки теории"""
        return await self.admin_repository.get_theory_cards(
            skip=skip,
            limit=limit,
            category=category,
            search=search
        )
    
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
        return await self.admin_repository.create_theory_card(
            anki_guid=anki_guid,
            card_type=card_type,
            deck=deck,
            category=category,
            sub_category=sub_category,
            question_block=question_block,
            answer_block=answer_block,
            tags=tags,
            order_index=order_index
        )
    
    async def update_theory_card(
        self,
        card_id: str,
        anki_guid: Optional[str] = None,
        card_type: Optional[str] = None,
        deck: Optional[str] = None,
        category: Optional[str] = None,
        sub_category: Optional[str] = None,
        question_block: Optional[str] = None,
        answer_block: Optional[str] = None,
        tags: Optional[List[str]] = None,
        order_index: Optional[int] = None
    ) -> Optional[AdminTheoryCard]:
        """Обновить карточку теории"""
        updates = {}
        
        if anki_guid is not None:
            updates["anki_guid"] = anki_guid
        if card_type is not None:
            updates["card_type"] = card_type
        if deck is not None:
            updates["deck"] = deck
        if category is not None:
            updates["category"] = category
        if sub_category is not None:
            updates["sub_category"] = sub_category
        if question_block is not None:
            updates["question_block"] = question_block
        if answer_block is not None:
            updates["answer_block"] = answer_block
        if tags is not None:
            updates["tags"] = tags
        if order_index is not None:
            updates["order_index"] = order_index
        
        return await self.admin_repository.update_theory_card(card_id, updates)
    
    async def delete_theory_card(self, card_id: str) -> bool:
        """Удалить карточку теории"""
        return await self.admin_repository.delete_theory_card(card_id)
    
    async def bulk_delete_content(self, ids: List[str]) -> BulkDeleteResult:
        """Массово удалить контент"""
        return await self.admin_repository.bulk_delete_content(ids)
    
    async def bulk_delete_theory(self, ids: List[str]) -> BulkDeleteResult:
        """Массово удалить теорию"""
        return await self.admin_repository.bulk_delete_theory(ids)
    
    def unescape_text_content(self, text: Optional[str]) -> Optional[str]:
        """Заменяет экранированные символы на настоящие переносы строк"""
        if not text:
            return text
        return text.replace("\\n", "\n").replace("\\t", "\t") 