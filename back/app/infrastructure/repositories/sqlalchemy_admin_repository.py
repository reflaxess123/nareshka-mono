"""SQLAlchemy implementation of AdminRepository."""

from typing import List, Optional, Dict, Any
from sqlalchemy import func, desc, or_, and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import uuid

from ...domain.repositories.admin_repository import AdminRepository
from ...domain.entities.admin import (
    SystemStats, UserStats, ContentStats, TheoryStats,
    AdminContentFile, AdminContentBlock, AdminTheoryCard,
    AdminUser, BulkDeleteResult
)
from ...domain.entities.user import User
from ...domain.entities.content import ContentFile, ContentBlock, UserContentProgress
from ...domain.entities.theory import TheoryCard, UserTheoryProgress


class SQLAlchemyAdminRepository(AdminRepository):
    """SQLAlchemy реализация AdminRepository"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def get_system_stats(self) -> SystemStats:
        """Получить общую статистику системы"""
        try:
            # Статистика пользователей
            users_stats = self.session.query(
                User.role, func.count(User.id)
            ).group_by(User.role).all()
            
            total_users = self.session.query(User).count()
            
            users_by_role = {"admin": 0, "user": 0, "guest": 0}
            for role, count in users_stats:
                users_by_role[role.lower()] = count
            
            # Статистика контента
            total_files = self.session.query(ContentFile).count()
            total_blocks = self.session.query(ContentBlock).count()
            total_theory_cards = self.session.query(TheoryCard).count()
            
            # Статистика прогресса
            total_content_progress = self.session.query(UserContentProgress).count()
            total_theory_progress = self.session.query(UserTheoryProgress).count()
            
            return SystemStats(
                users={
                    "total": total_users,
                    "admins": users_by_role["admin"],
                    "regularUsers": users_by_role["user"],
                    "guests": users_by_role["guest"]
                },
                content={
                    "totalFiles": total_files,
                    "totalBlocks": total_blocks,
                    "totalTheoryCards": total_theory_cards
                },
                progress={
                    "totalContentProgress": total_content_progress,
                    "totalTheoryProgress": total_theory_progress
                }
            )
        except SQLAlchemyError as e:
            raise Exception(f"Ошибка получения статистики: {str(e)}")
    
    async def get_users_with_stats(
        self, 
        skip: int = 0, 
        limit: int = 20,
        role: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[UserStats], int]:
        """Получить пользователей с подсчетом прогресса"""
        try:
            # Строим запрос
            query = self.session.query(User)
            
            if role:
                query = query.filter(User.role == role)
            
            if search:
                query = query.filter(User.email.ilike(f"%{search}%"))
            
            # Получаем общее количество
            total = query.count()
            
            # Получаем пользователей
            users = query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()
            
            # Добавляем подсчет прогресса для каждого пользователя
            users_with_stats = []
            for user in users:
                content_progress_count = self.session.query(UserContentProgress).filter(
                    UserContentProgress.user_id == user.id
                ).count()
                
                theory_progress_count = self.session.query(UserTheoryProgress).filter(
                    UserTheoryProgress.user_id == user.id
                ).count()
                
                users_with_stats.append(UserStats(
                    id=user.id,
                    email=user.email,
                    role=user.role,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                    content_progress_count=content_progress_count,
                    theory_progress_count=theory_progress_count
                ))
            
            return users_with_stats, total
            
        except SQLAlchemyError as e:
            raise Exception(f"Ошибка получения пользователей: {str(e)}")
    
    async def create_user(self, email: str, password_hash: str, role: str) -> AdminUser:
        """Создать нового пользователя"""
        try:
            # Проверяем существование пользователя
            existing_user = self.session.query(User).filter(User.email == email).first()
            if existing_user:
                raise Exception("Пользователь с таким email уже существует")
            
            user = User(
                id=str(uuid.uuid4()),
                email=email,
                password_hash=password_hash,
                role=role,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.session.add(user)
            self.session.commit()
            
            return AdminUser(
                id=user.id,
                email=user.email,
                role=user.role,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Ошибка создания пользователя: {str(e)}")
    
    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> Optional[AdminUser]:
        """Обновить пользователя"""
        try:
            user = self.session.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            for key, value in updates.items():
                if hasattr(user, key) and value is not None:
                    setattr(user, key, value)
            
            user.updated_at = datetime.utcnow()
            self.session.commit()
            
            return AdminUser(
                id=user.id,
                email=user.email,
                role=user.role,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Ошибка обновления пользователя: {str(e)}")
    
    async def delete_user(self, user_id: str) -> bool:
        """Удалить пользователя"""
        try:
            user = self.session.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            self.session.delete(user)
            self.session.commit()
            return True
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Ошибка удаления пользователя: {str(e)}")
    
    async def get_content_stats(self) -> ContentStats:
        """Получить статистику контента"""
        try:
            total_files = self.session.query(ContentFile).count()
            total_blocks = self.session.query(ContentBlock).count()
            
            # Файлы по категориям
            files_by_category = {}
            files_stats = self.session.query(
                ContentFile.main_category,
                func.count(ContentFile.id)
            ).group_by(ContentFile.main_category).all()
            
            for category, count in files_stats:
                files_by_category[category] = count
            
            # Блоки по категориям через файлы
            blocks_by_category = {}
            blocks_stats = self.session.query(
                ContentFile.main_category,
                func.count(ContentBlock.id)
            ).join(ContentBlock).group_by(ContentFile.main_category).all()
            
            for category, count in blocks_stats:
                blocks_by_category[category] = count
            
            return ContentStats(
                total_files=total_files,
                total_blocks=total_blocks,
                files_by_category=files_by_category,
                blocks_by_category=blocks_by_category
            )
            
        except SQLAlchemyError as e:
            raise Exception(f"Ошибка получения статистики контента: {str(e)}")
    
    async def get_content_files(
        self,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[AdminContentFile], int]:
        """Получить файлы контента"""
        try:
            query = self.session.query(ContentFile)
            
            if category:
                query = query.filter(ContentFile.main_category == category)
            
            if search:
                query = query.filter(
                    or_(
                        ContentFile.webdav_path.ilike(f"%{search}%"),
                        ContentFile.main_category.ilike(f"%{search}%"),
                        ContentFile.sub_category.ilike(f"%{search}%")
                    )
                )
            
            total = query.count()
            files = query.order_by(desc(ContentFile.created_at)).offset(skip).limit(limit).all()
            
            files_with_stats = []
            for file in files:
                blocks_count = self.session.query(ContentBlock).filter(
                    ContentBlock.file_id == file.id
                ).count()
                
                files_with_stats.append(AdminContentFile(
                    id=file.id,
                    webdav_path=file.webdav_path,
                    main_category=file.main_category,
                    sub_category=file.sub_category,
                    created_at=file.created_at,
                    updated_at=file.updated_at,
                    blocks_count=blocks_count
                ))
            
            return files_with_stats, total
            
        except SQLAlchemyError as e:
            raise Exception(f"Ошибка получения файлов контента: {str(e)}")
    
    async def create_content_file(
        self,
        webdav_path: str,
        main_category: str,
        sub_category: str
    ) -> AdminContentFile:
        """Создать файл контента"""
        try:
            file = ContentFile(
                id=str(uuid.uuid4()),
                webdav_path=webdav_path,
                main_category=main_category,
                sub_category=sub_category,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.session.add(file)
            self.session.commit()
            
            return AdminContentFile(
                id=file.id,
                webdav_path=file.webdav_path,
                main_category=file.main_category,
                sub_category=file.sub_category,
                created_at=file.created_at,
                updated_at=file.updated_at,
                blocks_count=0
            )
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Ошибка создания файла контента: {str(e)}")
    
    async def update_content_file(
        self,
        file_id: str,
        updates: Dict[str, Any]
    ) -> Optional[AdminContentFile]:
        """Обновить файл контента"""
        try:
            file = self.session.query(ContentFile).filter(ContentFile.id == file_id).first()
            if not file:
                return None
            
            for key, value in updates.items():
                if hasattr(file, key) and value is not None:
                    setattr(file, key, value)
            
            file.updated_at = datetime.utcnow()
            self.session.commit()
            
            blocks_count = self.session.query(ContentBlock).filter(
                ContentBlock.file_id == file.id
            ).count()
            
            return AdminContentFile(
                id=file.id,
                webdav_path=file.webdav_path,
                main_category=file.main_category,
                sub_category=file.sub_category,
                created_at=file.created_at,
                updated_at=file.updated_at,
                blocks_count=blocks_count
            )
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Ошибка обновления файла контента: {str(e)}")
    
    async def delete_content_file(self, file_id: str) -> bool:
        """Удалить файл контента"""
        try:
            file = self.session.query(ContentFile).filter(ContentFile.id == file_id).first()
            if not file:
                return False
            
            self.session.delete(file)
            self.session.commit()
            return True
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Ошибка удаления файла контента: {str(e)}")
    
    async def get_content_blocks(
        self,
        skip: int = 0,
        limit: int = 20,
        file_id: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[AdminContentBlock], int]:
        """Получить блоки контента"""
        try:
            query = self.session.query(ContentBlock)
            
            if file_id:
                query = query.filter(ContentBlock.file_id == file_id)
            
            if search:
                query = query.filter(
                    or_(
                        ContentBlock.block_title.ilike(f"%{search}%"),
                        ContentBlock.text_content.ilike(f"%{search}%"),
                        ContentBlock.code_content.ilike(f"%{search}%")
                    )
                )
            
            total = query.count()
            blocks = query.order_by(desc(ContentBlock.created_at)).offset(skip).limit(limit).all()
            
            admin_blocks = []
            for block in blocks:
                admin_blocks.append(AdminContentBlock(
                    id=block.id,
                    file_id=block.file_id,
                    path_titles=block.path_titles,
                    block_title=block.block_title,
                    block_level=block.block_level,
                    order_in_file=block.order_in_file,
                    text_content=block.text_content,
                    code_content=block.code_content,
                    code_language=block.code_language,
                    is_code_foldable=block.is_code_foldable,
                    code_fold_title=block.code_fold_title,
                    extracted_urls=block.extracted_urls,
                    created_at=block.created_at,
                    updated_at=block.updated_at
                ))
            
            return admin_blocks, total
            
        except SQLAlchemyError as e:
            raise Exception(f"Ошибка получения блоков контента: {str(e)}")
    
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
        try:
            block = ContentBlock(
                id=str(uuid.uuid4()),
                file_id=file_id,
                path_titles=path_titles or [],
                block_title=block_title,
                block_level=block_level,
                order_in_file=order_in_file,
                text_content=text_content,
                code_content=code_content,
                code_language=code_language,
                is_code_foldable=is_code_foldable,
                code_fold_title=code_fold_title,
                extracted_urls=extracted_urls or [],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.session.add(block)
            self.session.commit()
            
            return AdminContentBlock(
                id=block.id,
                file_id=block.file_id,
                path_titles=block.path_titles,
                block_title=block.block_title,
                block_level=block.block_level,
                order_in_file=block.order_in_file,
                text_content=block.text_content,
                code_content=block.code_content,
                code_language=block.code_language,
                is_code_foldable=block.is_code_foldable,
                code_fold_title=block.code_fold_title,
                extracted_urls=block.extracted_urls,
                created_at=block.created_at,
                updated_at=block.updated_at
            )
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Ошибка создания блока контента: {str(e)}")
    
    async def update_content_block(
        self,
        block_id: str,
        updates: Dict[str, Any]
    ) -> Optional[AdminContentBlock]:
        """Обновить блок контента"""
        try:
            block = self.session.query(ContentBlock).filter(ContentBlock.id == block_id).first()
            if not block:
                return None
            
            for key, value in updates.items():
                if hasattr(block, key) and value is not None:
                    setattr(block, key, value)
            
            block.updated_at = datetime.utcnow()
            self.session.commit()
            
            return AdminContentBlock(
                id=block.id,
                file_id=block.file_id,
                path_titles=block.path_titles,
                block_title=block.block_title,
                block_level=block.block_level,
                order_in_file=block.order_in_file,
                text_content=block.text_content,
                code_content=block.code_content,
                code_language=block.code_language,
                is_code_foldable=block.is_code_foldable,
                code_fold_title=block.code_fold_title,
                extracted_urls=block.extracted_urls,
                created_at=block.created_at,
                updated_at=block.updated_at
            )
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Ошибка обновления блока контента: {str(e)}")
    
    async def delete_content_block(self, block_id: str) -> bool:
        """Удалить блок контента"""
        try:
            block = self.session.query(ContentBlock).filter(ContentBlock.id == block_id).first()
            if not block:
                return False
            
            self.session.delete(block)
            self.session.commit()
            return True
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Ошибка удаления блока контента: {str(e)}")
    
    async def get_theory_cards(
        self,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[AdminTheoryCard], int]:
        """Получить карточки теории"""
        try:
            query = self.session.query(TheoryCard)
            
            if category:
                query = query.filter(TheoryCard.category == category)
            
            if search:
                query = query.filter(
                    or_(
                        TheoryCard.question_block.ilike(f"%{search}%"),
                        TheoryCard.answer_block.ilike(f"%{search}%"),
                        TheoryCard.category.ilike(f"%{search}%")
                    )
                )
            
            total = query.count()
            cards = query.order_by(desc(TheoryCard.created_at)).offset(skip).limit(limit).all()
            
            admin_cards = []
            for card in cards:
                admin_cards.append(AdminTheoryCard(
                    id=card.id,
                    anki_guid=card.anki_guid,
                    card_type=card.card_type,
                    deck=card.deck,
                    category=card.category,
                    sub_category=card.sub_category,
                    question_block=card.question_block,
                    answer_block=card.answer_block,
                    tags=card.tags,
                    order_index=card.order_index,
                    created_at=card.created_at,
                    updated_at=card.updated_at
                ))
            
            return admin_cards, total
            
        except SQLAlchemyError as e:
            raise Exception(f"Ошибка получения карточек теории: {str(e)}")
    
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
        try:
            card = TheoryCard(
                id=str(uuid.uuid4()),
                anki_guid=anki_guid,
                card_type=card_type,
                deck=deck,
                category=category,
                sub_category=sub_category,
                question_block=question_block,
                answer_block=answer_block,
                tags=tags,
                order_index=order_index,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.session.add(card)
            self.session.commit()
            
            return AdminTheoryCard(
                id=card.id,
                anki_guid=card.anki_guid,
                card_type=card.card_type,
                deck=card.deck,
                category=card.category,
                sub_category=card.sub_category,
                question_block=card.question_block,
                answer_block=card.answer_block,
                tags=card.tags,
                order_index=card.order_index,
                created_at=card.created_at,
                updated_at=card.updated_at
            )
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Ошибка создания карточки теории: {str(e)}")
    
    async def update_theory_card(
        self,
        card_id: str,
        updates: Dict[str, Any]
    ) -> Optional[AdminTheoryCard]:
        """Обновить карточку теории"""
        try:
            card = self.session.query(TheoryCard).filter(TheoryCard.id == card_id).first()
            if not card:
                return None
            
            for key, value in updates.items():
                if hasattr(card, key) and value is not None:
                    setattr(card, key, value)
            
            card.updated_at = datetime.utcnow()
            self.session.commit()
            
            return AdminTheoryCard(
                id=card.id,
                anki_guid=card.anki_guid,
                card_type=card.card_type,
                deck=card.deck,
                category=card.category,
                sub_category=card.sub_category,
                question_block=card.question_block,
                answer_block=card.answer_block,
                tags=card.tags,
                order_index=card.order_index,
                created_at=card.created_at,
                updated_at=card.updated_at
            )
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Ошибка обновления карточки теории: {str(e)}")
    
    async def delete_theory_card(self, card_id: str) -> bool:
        """Удалить карточку теории"""
        try:
            card = self.session.query(TheoryCard).filter(TheoryCard.id == card_id).first()
            if not card:
                return False
            
            self.session.delete(card)
            self.session.commit()
            return True
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Ошибка удаления карточки теории: {str(e)}")
    
    async def bulk_delete_content(self, ids: List[str]) -> BulkDeleteResult:
        """Массово удалить контент"""
        try:
            deleted_count = 0
            failed_ids = []
            error_messages = []
            
            for content_id in ids:
                try:
                    # Пытаемся удалить как файл
                    file = self.session.query(ContentFile).filter(ContentFile.id == content_id).first()
                    if file:
                        self.session.delete(file)
                        deleted_count += 1
                        continue
                    
                    # Пытаемся удалить как блок
                    block = self.session.query(ContentBlock).filter(ContentBlock.id == content_id).first()
                    if block:
                        self.session.delete(block)
                        deleted_count += 1
                        continue
                    
                    # Не найден
                    failed_ids.append(content_id)
                    error_messages.append(f"Контент с ID {content_id} не найден")
                    
                except Exception as e:
                    failed_ids.append(content_id)
                    error_messages.append(f"Ошибка удаления {content_id}: {str(e)}")
            
            if deleted_count > 0:
                self.session.commit()
            
            return BulkDeleteResult(
                deleted_count=deleted_count,
                failed_ids=failed_ids,
                error_messages=error_messages
            )
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Ошибка массового удаления контента: {str(e)}")
    
    async def bulk_delete_theory(self, ids: List[str]) -> BulkDeleteResult:
        """Массово удалить теорию"""
        try:
            deleted_count = 0
            failed_ids = []
            error_messages = []
            
            for card_id in ids:
                try:
                    card = self.session.query(TheoryCard).filter(TheoryCard.id == card_id).first()
                    if card:
                        self.session.delete(card)
                        deleted_count += 1
                    else:
                        failed_ids.append(card_id)
                        error_messages.append(f"Карточка с ID {card_id} не найдена")
                        
                except Exception as e:
                    failed_ids.append(card_id)
                    error_messages.append(f"Ошибка удаления {card_id}: {str(e)}")
            
            if deleted_count > 0:
                self.session.commit()
            
            return BulkDeleteResult(
                deleted_count=deleted_count,
                failed_ids=failed_ids,
                error_messages=error_messages
            )
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Ошибка массового удаления теории: {str(e)}") 