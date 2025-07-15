"""Реализация репозитория контента для SQLAlchemy"""

from datetime import datetime
from typing import List, Optional, Tuple
from uuid import uuid4

from sqlalchemy import and_, asc, desc, func, or_
from sqlalchemy.orm import Session, joinedload

from app.domain.repositories.content_repository import ContentRepository
from app.infrastructure.models.content_models import (
    ContentBlock,
    ContentFile,
    UserContentProgress,
)


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
        webdav_path: Optional[str] = None,
    ) -> Tuple[List[ContentFile], int]:
        """Получение файлов контента с пагинацией"""
        offset = (page - 1) * limit

        query = self.session.query(ContentFile)

        if main_category:
            query = query.filter(
                func.lower(ContentFile.mainCategory) == func.lower(main_category)
            )

        if sub_category:
            query = query.filter(
                func.lower(ContentFile.subCategory) == func.lower(sub_category)
            )

        if webdav_path:
            query = query.filter(ContentFile.webdavPath.ilike(f"%{webdav_path}%"))

        total = query.count()
        files = query.order_by(ContentFile.webdavPath).offset(offset).limit(limit).all()

        return files, total

    async def get_content_blocks(  # noqa: PLR0912
        self,
        page: int = 1,
        limit: int = 10,
        webdav_path: Optional[str] = None,
        main_category: Optional[str] = None,
        sub_category: Optional[str] = None,
        file_path_id: Optional[str] = None,
        search_query: Optional[str] = None,
        sort_by: str = "orderInFile",
        sort_order: str = "asc",
    ) -> Tuple[List[ContentBlock], int]:
        """Получение блоков контента с пагинацией и фильтрацией"""
        offset = (page - 1) * limit

        query = self.session.query(ContentBlock).join(ContentFile)

        # Фильтры
        if webdav_path:
            query = query.filter(ContentFile.webdavPath.ilike(f"%{webdav_path}%"))

        if main_category:
            query = query.filter(
                func.lower(ContentFile.mainCategory) == func.lower(main_category)
            )

        if sub_category:
            query = query.filter(
                func.lower(ContentFile.subCategory) == func.lower(sub_category)
            )

        if file_path_id:
            query = query.filter(ContentFile.id == file_path_id)

        # Поиск
        if search_query and search_query.strip():
            search_term = f"%{search_query.strip()}%"
            query = query.filter(
                or_(
                    ContentBlock.blockTitle.ilike(search_term),
                    ContentBlock.textContent.ilike(search_term),
                    ContentBlock.codeFoldTitle.ilike(search_term),
                )
            )

        # Сортировка
        if sort_by == "createdAt":
            order_field = ContentBlock.createdAt
        elif sort_by == "updatedAt":
            order_field = ContentBlock.updatedAt
        elif sort_by == "orderInFile":
            order_field = ContentBlock.orderInFile
        elif sort_by == "blockLevel":
            order_field = ContentBlock.blockLevel
        elif sort_by == "file.webdavPath":
            order_field = ContentFile.webdavPath
        else:
            order_field = ContentBlock.orderInFile

        if sort_order == "desc":
            query = query.order_by(desc(order_field))
        else:
            query = query.order_by(asc(order_field))

        total = query.count()
        blocks = (
            query.options(joinedload(ContentBlock.file))
            .offset(offset)
            .limit(limit)
            .all()
        )

        return blocks, total

    async def get_content_block_by_id(self, block_id: str) -> Optional[ContentBlock]:
        """Получение блока контента по ID"""
        return (
            self.session.query(ContentBlock)
            .options(joinedload(ContentBlock.file))
            .filter(ContentBlock.id == block_id)
            .first()
        )

    async def get_content_categories(self) -> List[str]:
        """Получение списка основных категорий"""
        return [
            row[0]
            for row in self.session.query(ContentFile.mainCategory)
            .distinct()
            .order_by(ContentFile.mainCategory)
            .all()
        ]

    async def get_content_subcategories(self, category: str) -> List[str]:
        """Получение списка подкатегорий для категории"""
        return [
            row[0]
            for row in self.session.query(ContentFile.subCategory)
            .filter(func.lower(ContentFile.mainCategory) == func.lower(category))
            .distinct()
            .order_by(ContentFile.subCategory)
            .all()
        ]

    async def get_user_content_progress(
        self, user_id: int, block_id: str
    ) -> Optional[UserContentProgress]:
        """Получение прогресса пользователя по блоку"""
        return (
            self.session.query(UserContentProgress)
            .filter(
                and_(
                    UserContentProgress.userId == user_id,
                    UserContentProgress.blockId == block_id,
                )
            )
            .first()
        )

    async def create_or_update_user_progress(
        self, user_id: int, block_id: str, solved_count: int
    ) -> UserContentProgress:
        """Создание или обновление прогресса пользователя"""
        progress = (
            self.session.query(UserContentProgress)
            .filter(
                and_(
                    UserContentProgress.userId == user_id,
                    UserContentProgress.blockId == block_id,
                )
            )
            .first()
        )

        if progress:
            progress.solvedCount = solved_count
            progress.updatedAt = datetime.utcnow()
        else:
            progress = UserContentProgress(
                id=str(uuid4()),
                userId=user_id,
                blockId=block_id,
                solvedCount=solved_count,
                createdAt=datetime.utcnow(),
                updatedAt=datetime.utcnow(),
            )
            self.session.add(progress)

        return progress

    async def get_user_total_solved_count(self, user_id: int) -> int:
        """Получение общего количества решенных задач пользователя"""
        return (
            self.session.query(func.count(UserContentProgress.id))
            .filter(
                and_(
                    UserContentProgress.userId == user_id,
                    UserContentProgress.solvedCount > 0,
                )
            )
            .join(ContentBlock)
            .join(ContentFile)
            .filter(
                and_(
                    ContentFile.mainCategory != "Test",
                    ContentFile.subCategory != "Test",
                )
            )
            .scalar()
            or 0
        )
