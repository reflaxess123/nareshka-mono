"""Репозиторий для работы с блоками контента"""

import logging
from typing import List, Optional, Tuple

from sqlalchemy import asc, or_
from sqlalchemy.orm import Session, joinedload

from app.shared.models.content_models import ContentBlock
from app.shared.schemas.task import Task
from app.shared.models.content_models import UserContentProgress

logger = logging.getLogger(__name__)


class ContentBlockRepository:
    """Репозиторий для работы с блоками контента"""

    def __init__(self, session: Session):
        self.session = session

    def _unescape_text_content(self, text: Optional[str]) -> Optional[str]:
        """Заменяет экранированные символы на настоящие переносы строк"""
        if not text:
            return text
        return text.replace("\\n", "\n").replace("\\t", "\t")

    def get_content_blocks(
        self,
        user_id: Optional[int] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        company: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Tuple[List[Task], int]:
        """Получить блоки контента с фильтрацией"""

        # Базовый запрос с загрузкой связанных данных
        query = (
            self.session.query(ContentBlock)
            .options(joinedload(ContentBlock.files))
            .filter(ContentBlock.is_deleted == False)
        )

        # Фильтрация по категории
        if category:
            query = query.filter(ContentBlock.category == category)

        # Поиск по названию и содержимому
        if search:
            search_filter = or_(
                ContentBlock.title.ilike(f"%{search}%"),
                ContentBlock.content.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        # Фильтрация по компании
        if company:
            query = query.filter(ContentBlock.company == company)

        # Подсчет общего количества
        total_count = query.count()

        # Применение пагинации
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        # Сортировка по order_in_file
        query = query.order_by(asc(ContentBlock.order_in_file))

        content_blocks = query.all()

        # Получение прогресса пользователя для блоков контента
        user_progress = {}
        if user_id:
            progress_query = (
                self.session.query(UserContentProgress)
                .filter(UserContentProgress.user_id == user_id)
                .filter(
                    UserContentProgress.content_block_id.in_(
                        [cb.id for cb in content_blocks]
                    )
                )
            )
            user_progress_records = progress_query.all()
            user_progress = {up.content_block_id: up for up in user_progress_records}

        # Преобразование в объекты Task
        tasks = []
        for block in content_blocks:
            progress = user_progress.get(block.id)

            # Подготовка файлов
            files = []
            if block.files:
                for file in block.files:
                    files.append(
                        {
                            "id": file.id,
                            "filename": file.filename,
                            "content": self._unescape_text_content(file.content),
                            "language": self._map_language(file.language),
                            "type": file.type,
                            "order_in_block": file.order_in_block,
                        }
                    )

            task = Task(
                id=block.id,
                title=block.blockTitle,
                content=self._unescape_text_content(block.content),
                category=block.category,
                company=block.company,
                language=block.language,
                difficulty=block.difficulty,
                type="content_block",
                order_in_file=block.order_in_file,
                files=files,
                is_completed=progress.is_completed if progress else False,
                progress_percentage=progress.progress_percentage if progress else 0,
                time_spent=progress.time_spent if progress else 0,
                last_viewed=progress.last_viewed if progress else None,
                attempts_count=progress.attempts_count if progress else 0,
            )
            tasks.append(task)

        return tasks, total_count

    def _map_language(self, language: Optional[str]) -> Optional[str]:
        """Маппинг языков программирования для корректного отображения"""
        if not language:
            return None

        language_mapping = {
            "js": "javascript",
            "ts": "typescript",
            "py": "python",
            "cpp": "cpp",
            "c": "c",
            "java": "java",
            "go": "go",
            "rust": "rust",
            "php": "php",
            "rb": "ruby",
            "kt": "kotlin",
            "swift": "swift",
            "scala": "scala",
            "sh": "bash",
            "sql": "sql",
            "html": "html",
            "css": "css",
            "xml": "xml",
            "json": "json",
            "yaml": "yaml",
            "yml": "yaml",
            "md": "markdown",
            "dockerfile": "dockerfile",
        }

        return language_mapping.get(language.lower(), language)

    def get_content_block_categories(self) -> List[str]:
        """Получить список уникальных категорий блоков контента"""
        categories = (
            self.session.query(ContentBlock.category)
            .filter(ContentBlock.is_deleted == False)
            .filter(ContentBlock.category.isnot(None))
            .distinct()
            .all()
        )
        return [cat[0] for cat in categories if cat[0]]

    def get_content_block_companies(self) -> List[str]:
        """Получить список уникальных компаний блоков контента"""
        companies = (
            self.session.query(ContentBlock.company)
            .filter(ContentBlock.is_deleted == False)
            .filter(ContentBlock.company.isnot(None))
            .distinct()
            .all()
        )
        return [comp[0] for comp in companies if comp[0]]
