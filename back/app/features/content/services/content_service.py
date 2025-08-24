"""
Content Service - бизнес-логика для работы с контентом

Содержит всю бизнес-логику для работы с образовательным контентом:
- Получение файлов и блоков контента
- Управление прогрессом пользователя
- Работа с категориями и поиском
"""

from typing import List, Optional, Tuple

from app.core.logging import get_logger
from app.features.content.dto.requests import ProgressAction
from app.features.content.dto.responses import (
    ContentBlockResponse,
    ContentBlockWithProgressResponse,
    ContentFileResponse,
)
from app.features.content.exceptions.content_exceptions import (
    InvalidProgressActionError,
)
from app.features.content.repositories.content_repository import ContentRepository
from app.shared.models.content_models import UserContentProgress as ContentBlockProgress

logger = get_logger(__name__)


class ContentService:
    """Сервис для работы с образовательным контентом"""

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
        """Получение файлов контента с пагинацией и фильтрацией"""
        logger.debug(
            "Getting content files",
            extra={
                "page": page,
                "limit": limit,
                "main_category": main_category,
                "sub_category": sub_category,
                "webdav_path": webdav_path,
            },
        )

        files, total = await self.content_repository.get_content_files(
            page=page,
            limit=limit,
            main_category=main_category,
            sub_category=sub_category,
            webdav_path=webdav_path,
        )

        # Конвертируем в response DTOs
        file_responses = [
            ContentFileResponse(
                id=file.id,
                createdAt=file.createdAt,
                updatedAt=file.updatedAt,
                webdavPath=file.webdavPath,
                mainCategory=file.mainCategory,
                subCategory=file.subCategory,
                lastFileHash=file.lastFileHash,
            )
            for file in files
        ]

        logger.info(f"Retrieved {len(file_responses)} content files (total: {total})")
        return file_responses, total

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
        """Получение блоков контента с пагинацией, фильтрацией и прогрессом пользователя"""
        logger.debug(
            "Getting content blocks",
            extra={
                "page": page,
                "limit": limit,
                "user_id": user_id,
                "search_query": search_query,
                "sort_by": sort_by,
            },
        )

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

                # Создаем response с прогрессом
                block_response = ContentBlockWithProgressResponse(
                    id=block.id,
                    createdAt=block.createdAt,
                    updatedAt=block.updatedAt,
                    fileId=block.fileId,
                    pathTitles=block.pathTitles,
                    blockTitle=block.blockTitle,
                    blockLevel=block.blockLevel,
                    orderInFile=block.orderInFile,
                    textContent=block.textContent,
                    codeContent=block.codeContent,
                    codeLanguage=block.codeLanguage,
                    isCodeFoldable=block.isCodeFoldable,
                    codeFoldTitle=block.codeFoldTitle,
                    extractedUrls=block.extractedUrls,
                    companies=block.companies,
                    rawBlockContentHash=block.rawBlockContentHash,
                    userProgress=progress.solvedCount if progress else 0,
                )

                # Добавляем информацию о файле если доступна
                if hasattr(block, "file") and block.file:
                    block_response.file = ContentFileResponse(
                        id=block.file.id,
                        createdAt=block.file.createdAt,
                        updatedAt=block.file.updatedAt,
                        webdavPath=block.file.webdavPath,
                        mainCategory=block.file.mainCategory,
                        subCategory=block.file.subCategory,
                        lastFileHash=block.file.lastFileHash,
                    )

                block_responses.append(block_response)

            logger.info(
                f"Retrieved {len(block_responses)} content blocks with progress (total: {total})"
            )
            return block_responses, total
        else:
            # Без прогресса пользователя
            block_responses = []
            for block in blocks:
                block_response = ContentBlockResponse(
                    id=block.id,
                    createdAt=block.createdAt,
                    updatedAt=block.updatedAt,
                    fileId=block.fileId,
                    pathTitles=block.pathTitles,
                    blockTitle=block.blockTitle,
                    blockLevel=block.blockLevel,
                    orderInFile=block.orderInFile,
                    textContent=block.textContent,
                    codeContent=block.codeContent,
                    codeLanguage=block.codeLanguage,
                    isCodeFoldable=block.isCodeFoldable,
                    codeFoldTitle=block.codeFoldTitle,
                    extractedUrls=block.extractedUrls,
                    companies=block.companies,
                    rawBlockContentHash=block.rawBlockContentHash,
                )

                # Добавляем информацию о файле если доступна
                if hasattr(block, "file") and block.file:
                    block_response.file = ContentFileResponse(
                        id=block.file.id,
                        createdAt=block.file.createdAt,
                        updatedAt=block.file.updatedAt,
                        webdavPath=block.file.webdavPath,
                        mainCategory=block.file.mainCategory,
                        subCategory=block.file.subCategory,
                        lastFileHash=block.file.lastFileHash,
                    )

                block_responses.append(block_response)

            logger.info(
                f"Retrieved {len(block_responses)} content blocks (total: {total})"
            )
            return block_responses, total

    async def get_content_block_by_id(
        self, block_id: str, user_id: Optional[int] = None
    ) -> ContentBlockResponse:
        """Получение конкретного блока контента по ID"""
        logger.debug(f"Getting content block by ID: {block_id} (user_id: {user_id})")

        # Получаем блок (исключение будет выброшено автоматически если не найден)
        block = await self.content_repository.get_content_block_by_id(block_id)

        if user_id:
            # Получаем прогресс пользователя
            progress = await self.content_repository.get_user_content_progress(
                user_id, block_id
            )

            response = ContentBlockWithProgressResponse(
                id=block.id,
                createdAt=block.createdAt,
                updatedAt=block.updatedAt,
                fileId=block.fileId,
                pathTitles=block.pathTitles,
                blockTitle=block.blockTitle,
                blockLevel=block.blockLevel,
                orderInFile=block.orderInFile,
                textContent=block.textContent,
                codeContent=block.codeContent,
                codeLanguage=block.codeLanguage,
                isCodeFoldable=block.isCodeFoldable,
                codeFoldTitle=block.codeFoldTitle,
                extractedUrls=block.extractedUrls,
                companies=block.companies,
                rawBlockContentHash=block.rawBlockContentHash,
                userProgress=progress.solvedCount if progress else 0,
            )
        else:
            response = ContentBlockResponse(
                id=block.id,
                createdAt=block.createdAt,
                updatedAt=block.updatedAt,
                fileId=block.fileId,
                pathTitles=block.pathTitles,
                blockTitle=block.blockTitle,
                blockLevel=block.blockLevel,
                orderInFile=block.orderInFile,
                textContent=block.textContent,
                codeContent=block.codeContent,
                codeLanguage=block.codeLanguage,
                isCodeFoldable=block.isCodeFoldable,
                codeFoldTitle=block.codeFoldTitle,
                extractedUrls=block.extractedUrls,
                companies=block.companies,
                rawBlockContentHash=block.rawBlockContentHash,
            )

        # Добавляем информацию о файле
        if hasattr(block, "file") and block.file:
            response.file = ContentFileResponse(
                id=block.file.id,
                createdAt=block.file.createdAt,
                updatedAt=block.file.updatedAt,
                webdavPath=block.file.webdavPath,
                mainCategory=block.file.mainCategory,
                subCategory=block.file.subCategory,
                lastFileHash=block.file.lastFileHash,
            )

        logger.info(f"Retrieved content block: {block.blockTitle}")
        return response

    async def get_content_categories(self) -> List[str]:
        """Получение списка всех основных категорий контента"""
        logger.debug("Getting content categories")

        categories = await self.content_repository.get_content_categories()

        logger.info(f"Retrieved {len(categories)} content categories")
        return categories

    async def get_content_subcategories(self, category: str) -> List[str]:
        """Получение списка подкатегорий для указанной категории"""
        logger.debug(f"Getting subcategories for category: {category}")

        subcategories = await self.content_repository.get_content_subcategories(
            category
        )

        logger.info(f"Retrieved {len(subcategories)} subcategories for '{category}'")
        return subcategories

    async def update_content_block_progress(
        self, block_id: str, user_id: int, action: ProgressAction
    ) -> ContentBlockProgress:
        """Обновление прогресса пользователя по блоку контента"""
        logger.debug(
            f"Updating content progress: block_id={block_id}, user_id={user_id}, action={action.action}"
        )

        # Проверяем существование блока (исключение выбросится автоматически)
        await self.content_repository.get_content_block_by_id(block_id)

        # Получаем текущий прогресс
        current_progress = await self.content_repository.get_user_content_progress(
            user_id, block_id
        )
        current_count = current_progress.solvedCount if current_progress else 0

        # Вычисляем новое значение
        if action.action == "increment":
            new_count = current_count + 1
        elif action.action == "decrement":
            new_count = max(0, current_count - 1)
        else:
            raise InvalidProgressActionError(action.action)

        # Сохраняем новый прогресс
        progress = await self.content_repository.create_or_update_user_progress(
            user_id=user_id, block_id=block_id, solved_count=new_count
        )

        logger.info(
            f"Updated content progress: {current_count} -> {new_count}",
            extra={"user_id": user_id, "block_id": block_id, "action": action.action},
        )

        return progress

    async def get_user_total_solved_count(self, user_id: int) -> int:
        """Получение общего количества решенных блоков пользователем"""
        logger.debug(f"Getting total solved count for user: {user_id}")

        count = await self.content_repository.get_user_total_solved_count(user_id)

        logger.info(f"User {user_id} has solved {count} content blocks")
        return count

    @staticmethod
    def unescape_text_content(text: Optional[str]) -> Optional[str]:
        """Утилитарная функция для обработки экранированных символов в тексте"""
        if not text:
            return text
        return text.replace("\\n", "\n").replace("\\t", "\t")
