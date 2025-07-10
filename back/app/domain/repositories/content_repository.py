"""Интерфейс репозитория для работы с контентом"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from app.infrastructure.models.content_models import (
    ContentBlock,
    ContentFile,
    UserContentProgress,
)


class ContentRepository(ABC):
    """Абстрактный репозиторий для работы с контентом"""

    @abstractmethod
    async def get_content_files(
        self,
        page: int = 1,
        limit: int = 10,
        main_category: Optional[str] = None,
        sub_category: Optional[str] = None,
        webdav_path: Optional[str] = None,
    ) -> Tuple[List[ContentFile], int]:
        """Получение файлов контента с пагинацией"""
        pass

    @abstractmethod
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
        sort_order: str = "asc",
    ) -> Tuple[List[ContentBlock], int]:
        """Получение блоков контента с пагинацией и фильтрацией"""
        pass

    @abstractmethod
    async def get_content_block_by_id(self, block_id: str) -> Optional[ContentBlock]:
        """Получение блока контента по ID"""
        pass

    @abstractmethod
    async def get_content_categories(self) -> List[str]:
        """Получение списка основных категорий"""
        pass

    @abstractmethod
    async def get_content_subcategories(self, category: str) -> List[str]:
        """Получение списка подкатегорий для категории"""
        pass

    @abstractmethod
    async def get_user_content_progress(
        self, user_id: int, block_id: str
    ) -> Optional[UserContentProgress]:
        """Получение прогресса пользователя по блоку"""
        pass

    @abstractmethod
    async def create_or_update_user_progress(
        self, user_id: int, block_id: str, solved_count: int
    ) -> UserContentProgress:
        """Создание или обновление прогресса пользователя"""
        pass

    @abstractmethod
    async def get_user_total_solved_count(self, user_id: int) -> int:
        """Получение общего количества решенных задач пользователя"""
        pass
