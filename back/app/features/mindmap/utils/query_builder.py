"""Общие утилиты для построения SQL запросов"""

from typing import Optional, List, Dict
from sqlalchemy import func
from sqlalchemy.orm import Query, Session
from app.shared.models.content_models import ContentBlock, ContentFile
from app.shared.models.content_models import UserContentProgress


class ContentQueryBuilder:
    """Строитель запросов для работы с контентом"""

    @staticmethod
    def filter_by_category(
        query: Query,
        main_category: str,
        sub_category: Optional[str] = None
    ) -> Query:
        """Добавить фильтры по категориям"""
        query = query.filter(
            func.lower(ContentFile.mainCategory) == func.lower(main_category)
        )
        
        if sub_category:
            query = query.filter(
                func.lower(ContentFile.subCategory) == func.lower(sub_category)
            )
        
        return query

    @staticmethod
    def filter_with_code(query: Query) -> Query:
        """Фильтр только блоков с кодом"""
        return query.filter(ContentBlock.codeContent.isnot(None))

    @staticmethod 
    def join_content_file(query: Query) -> Query:
        """Добавить JOIN с ContentFile"""
        return query.join(ContentFile, ContentBlock.fileId == ContentFile.id)

    @staticmethod
    def get_content_blocks_with_code(
        session: Session,
        main_category: str,
        sub_category: Optional[str] = None
    ) -> Query:
        """Базовый запрос для блоков с кодом по категории"""
        query = session.query(ContentBlock)
        query = ContentQueryBuilder.join_content_file(query)
        query = ContentQueryBuilder.filter_with_code(query)
        query = ContentQueryBuilder.filter_by_category(query, main_category, sub_category)
        return query

    @staticmethod
    def count_completed_tasks(
        session: Session,
        user_id: int,
        main_category: str,
        sub_category: Optional[str] = None
    ) -> int:
        """Подсчет выполненных задач пользователем"""
        query = (
            session.query(func.count(UserContentProgress.id))
            .join(ContentBlock, UserContentProgress.blockId == ContentBlock.id)
            .join(ContentFile, ContentBlock.fileId == ContentFile.id)
            .filter(
                UserContentProgress.userId == user_id,
                UserContentProgress.solvedCount > 0,
                ContentBlock.codeContent.isnot(None)
            )
        )
        
        query = ContentQueryBuilder.filter_by_category(query, main_category, sub_category)
        return query.scalar() or 0

    @staticmethod
    def count_total_tasks(
        session: Session,
        main_category: str,
        sub_category: Optional[str] = None
    ) -> int:
        """Подсчет общего количества задач"""
        query = (
            session.query(func.count(ContentBlock.id))
            .join(ContentFile, ContentBlock.fileId == ContentFile.id)
            .filter(ContentBlock.codeContent.isnot(None))
        )
        
        query = ContentQueryBuilder.filter_by_category(query, main_category, sub_category)
        return query.scalar() or 0

    @staticmethod
    def get_bulk_user_progress(
        session: Session,
        user_id: int,
        block_ids: List[str]
    ) -> Dict[str, UserContentProgress]:
        """Получить прогресс пользователя для списка блоков одним запросом"""
        if not block_ids:
            return {}
            
        progress_records = (
            session.query(UserContentProgress)
            .filter(
                UserContentProgress.userId == user_id,
                UserContentProgress.blockId.in_(block_ids)
            )
            .all()
        )
        
        return {
            progress.blockId: progress 
            for progress in progress_records
        }