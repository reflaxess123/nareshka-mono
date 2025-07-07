"""Реализация репозитория контента для SQLAlchemy"""

from typing import List, Optional, Tuple
from uuid import uuid4
from datetime import datetime
from sqlalchemy import and_, func, or_, asc, desc
from sqlalchemy.orm import Session, joinedload

from ...domain.entities.content import ContentFile as DomainContentFile, ContentBlock as DomainContentBlock, UserContentProgress as DomainUserContentProgress
from ...domain.repositories.content_repository import ContentRepository
from ..models.content_models import ContentFile as InfraContentFile, ContentBlock as InfraContentBlock, UserContentProgress as InfraUserContentProgress
from ..mappers.content_mapper import ContentMapper


class SQLAlchemyContentRepository(ContentRepository):
    """Реализация репозитория контента для SQLAlchemy"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def get_content_files(
        self,
        page: int = 1,
        limit: int = 10,
        main_category: Optional[str] = None,
        sub_category: Optional[str] = None,
        webdav_path: Optional[str] = None
    ) -> Tuple[List[DomainContentFile], int]:
        """Получение файлов контента с пагинацией"""
        offset = (page - 1) * limit
        
        query = self.session.query(InfraContentFile)
        
        if main_category:
            query = query.filter(func.lower(InfraContentFile.mainCategory) == func.lower(main_category))
        
        if sub_category:
            query = query.filter(func.lower(InfraContentFile.subCategory) == func.lower(sub_category))
        
        if webdav_path:
            query = query.filter(InfraContentFile.webdavPath.ilike(f"%{webdav_path}%"))
        
        total = query.count()
        infra_files = query.order_by(InfraContentFile.webdavPath).offset(offset).limit(limit).all()
        
        domain_files = ContentMapper.content_file_list_to_domain(infra_files)
        return domain_files, total
    
    async def get_content_blocks(
        self,
        page: int = 1,
        limit: int = 10,
        webdav_path: Optional[str] = None,
        main_category: Optional[str] = None,
        sub_category: Optional[str] = None,
        file_path_id: Optional[str] = None,
        search_query: Optional[str] = None,
        sort_by: str = "orderInFile",
        sort_order: str = "asc"
    ) -> Tuple[List[DomainContentBlock], int]:
        """Получение блоков контента с пагинацией и фильтрацией"""
        offset = (page - 1) * limit
        
        query = self.session.query(InfraContentBlock).join(InfraContentFile)
        
        # Фильтры
        if webdav_path:
            query = query.filter(InfraContentFile.webdavPath.ilike(f"%{webdav_path}%"))
        
        if main_category:
            query = query.filter(func.lower(InfraContentFile.mainCategory) == func.lower(main_category))
        
        if sub_category:
            query = query.filter(func.lower(InfraContentFile.subCategory) == func.lower(sub_category))
        
        if file_path_id:
            query = query.filter(InfraContentFile.id == file_path_id)
        
        # Поиск
        if search_query and search_query.strip():
            search_term = f"%{search_query.strip()}%"
            query = query.filter(
                or_(
                    InfraContentBlock.blockTitle.ilike(search_term),
                    InfraContentBlock.textContent.ilike(search_term),
                    InfraContentBlock.codeFoldTitle.ilike(search_term)
                )
            )
        
        # Сортировка
        if sort_by == "createdAt":
            order_field = InfraContentBlock.createdAt
        elif sort_by == "updatedAt":
            order_field = InfraContentBlock.updatedAt
        elif sort_by == "orderInFile":
            order_field = InfraContentBlock.orderInFile
        elif sort_by == "blockLevel":
            order_field = InfraContentBlock.blockLevel
        elif sort_by == "file.webdavPath":
            order_field = InfraContentFile.webdavPath
        else:
            order_field = InfraContentBlock.orderInFile
        
        if sort_order == "desc":
            query = query.order_by(desc(order_field))
        else:
            query = query.order_by(asc(order_field))
        
        total = query.count()
        infra_blocks = query.options(joinedload(InfraContentBlock.file)).offset(offset).limit(limit).all()
        
        domain_blocks = ContentMapper.content_block_list_to_domain(infra_blocks)
        return domain_blocks, total
    
    async def get_content_block_by_id(self, block_id: str) -> Optional[DomainContentBlock]:
        """Получение блока контента по ID"""
        infra_block = self.session.query(InfraContentBlock).options(
            joinedload(InfraContentBlock.file)
        ).filter(InfraContentBlock.id == block_id).first()
        
        return ContentMapper.content_block_to_domain(infra_block) if infra_block else None
    
    async def get_content_categories(self) -> List[str]:
        """Получение списка основных категорий"""
        return [
            row[0] for row in self.session.query(InfraContentFile.mainCategory)
            .distinct()
            .order_by(InfraContentFile.mainCategory)
            .all()
        ]
    
    async def get_content_subcategories(self, category: str) -> List[str]:
        """Получение списка подкатегорий для категории"""
        return [
            row[0] for row in self.session.query(InfraContentFile.subCategory)
            .filter(func.lower(InfraContentFile.mainCategory) == func.lower(category))
            .distinct()
            .order_by(InfraContentFile.subCategory)
            .all()
        ]
    
    async def get_user_content_progress(
        self, 
        user_id: int, 
        block_id: str
    ) -> Optional[DomainUserContentProgress]:
        """Получение прогресса пользователя по блоку"""
        infra_progress = self.session.query(InfraUserContentProgress).filter(
            and_(
                InfraUserContentProgress.userId == user_id,
                InfraUserContentProgress.blockId == block_id
            )
        ).first()
        
        return ContentMapper.user_content_progress_to_domain(infra_progress) if infra_progress else None
    
    async def create_or_update_user_progress(
        self,
        user_id: int,
        block_id: str,
        solved_count: int
    ) -> DomainUserContentProgress:
        """Создание или обновление прогресса пользователя"""
        infra_progress = self.session.query(InfraUserContentProgress).filter(
            and_(
                InfraUserContentProgress.userId == user_id,
                InfraUserContentProgress.blockId == block_id
            )
        ).first()
        
        if infra_progress:
            infra_progress.solvedCount = solved_count
            infra_progress.updatedAt = datetime.utcnow()
        else:
            infra_progress = InfraUserContentProgress(
                id=str(uuid4()),
                userId=user_id,
                blockId=block_id,
                solvedCount=solved_count,
                createdAt=datetime.utcnow(),
                updatedAt=datetime.utcnow()
            )
            self.session.add(infra_progress)
        
        return ContentMapper.user_content_progress_to_domain(infra_progress)
    
    async def get_user_total_solved_count(self, user_id: int) -> int:
        """Получение общего количества решенных задач пользователя"""
        return self.session.query(func.count(InfraUserContentProgress.id)).filter(
            and_(
                InfraUserContentProgress.userId == user_id,
                InfraUserContentProgress.solvedCount > 0
            )
        ).join(InfraContentBlock).join(InfraContentFile).filter(
            and_(
                InfraContentFile.mainCategory != 'Test',
                InfraContentFile.subCategory != 'Test'
            )
        ).scalar() or 0 