"""Сервис для работы с контентом"""

from typing import List, Optional, Tuple

from fastapi import HTTPException, status

from app.application.dto.content_dto import (
    ContentBlockResponse,
    ContentBlockWithProgressResponse,
    ContentFileResponse,
    ProgressAction,
)
from app.domain.repositories.content_repository import ContentRepository
from app.infrastructure.models.content_models import (
    UserContentProgress,
)


class ContentService:
    """Сервис для работы с контентом"""

    def __init__(self, content_repository: ContentRepository):
        self.content_repository = content_repository

    async def get_content_files(
        self,
        page: int = 1,
        limit: int = 10,
        main_category: Optional[str] = None,
        sub_category: Optional[str] = None,
        webdav_path: Optional[str] = None,
    ) -> Tuple[List[ContentFileResponse], int]:
        """Получение файлов контента с пагинацией"""
        files, total = await self.content_repository.get_content_files(
            page=page,
            limit=limit,
            main_category=main_category,
            sub_category=sub_category,
            webdav_path=webdav_path,
        )

        return [ContentFileResponse.from_orm(file) for file in files], total

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
        user_id: Optional[int] = None,
    ) -> Tuple[List[ContentBlockResponse], int]:
        """Получение блоков контента с пагинацией и фильтрацией"""
        blocks, total = await self.content_repository.get_content_blocks(
            page=page,
            limit=limit,
            webdav_path=webdav_path,
            main_category=main_category,
            sub_category=sub_category,
            file_path_id=file_path_id,
            search_query=search_query,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        # Если пользователь аутентифицирован, добавляем прогресс
        if user_id:
            block_responses = []
            for block in blocks:
                progress = await self.content_repository.get_user_content_progress(
                    user_id, block.id
                )
                block_response = ContentBlockWithProgressResponse.from_orm(block)
                block_response.userProgress = progress.solvedCount if progress else 0
                block_responses.append(block_response)
            return block_responses, total
        else:
            return [ContentBlockResponse.from_orm(block) for block in blocks], total

    async def get_content_block_by_id(
        self, block_id: str, user_id: Optional[int] = None
    ) -> ContentBlockResponse:
        """Получение блока контента по ID"""
        block = await self.content_repository.get_content_block_by_id(block_id)

        if not block:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Content block not found"
            )

        if user_id:
            progress = await self.content_repository.get_user_content_progress(
                user_id, block_id
            )
            block_response = ContentBlockWithProgressResponse.from_orm(block)
            block_response.userProgress = progress.solvedCount if progress else 0
            return block_response
        else:
            return ContentBlockResponse.from_orm(block)

    async def get_content_categories(self) -> List[str]:
        """Получение списка основных категорий"""
        return await self.content_repository.get_content_categories()

    async def get_content_subcategories(self, category: str) -> List[str]:
        """Получение списка подкатегорий для категории"""
        return await self.content_repository.get_content_subcategories(category)

    async def update_content_block_progress(
        self, block_id: str, user_id: int, action: ProgressAction
    ) -> UserContentProgress:
        """Обновление прогресса пользователя по блоку"""
        # Проверяем существование блока
        block = await self.content_repository.get_content_block_by_id(block_id)
        if not block:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Content block not found"
            )

        # Получаем текущий прогресс
        current_progress = await self.content_repository.get_user_content_progress(
            user_id, block_id
        )
        current_count = current_progress.solvedCount if current_progress else 0

        # Обновляем счетчик
        if action.action == "increment":
            new_count = current_count + 1
        elif action.action == "decrement":
            new_count = max(0, current_count - 1)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid action. Use 'increment' or 'decrement'",
            )

        # Сохраняем новый прогресс
        progress = await self.content_repository.create_or_update_user_progress(
            user_id=user_id, block_id=block_id, solved_count=new_count
        )

        # Сохраняем изменения в базе данных
        if hasattr(self.content_repository, "session"):
            self.content_repository.session.commit()

        return progress

    async def get_user_total_solved_count(self, user_id: int) -> int:
        """Получение общего количества решенных задач пользователя"""
        return await self.content_repository.get_user_total_solved_count(user_id)
