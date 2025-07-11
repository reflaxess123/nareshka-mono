"""API для работы с контентом (новая архитектура)"""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.application.dto.content_dto import (
    ContentBlockResponse,
    ContentBlocksListResponse,
    ContentCategoriesResponse,
    ContentFilesListResponse,
    ContentSubcategoriesResponse,
    ProgressAction,
    UserContentProgressResponse,
)
from app.application.services.content_service import ContentService
from app.infrastructure.models.user_models import User
from app.shared.dependencies import (
    get_content_service,
    get_current_user_optional,
    get_current_user_required,
)

router = APIRouter(prefix="/content", tags=["content"])


def unescape_text_content(text: Optional[str]) -> Optional[str]:
    """Заменяет экранированные символы на настоящие переносы строк"""
    if not text:
        return text
    return text.replace("\\n", "\n").replace("\\t", "\t")


@router.get("/blocks", response_model=ContentBlocksListResponse)
async def get_content_blocks(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=100, description="Количество блоков на странице"),
    webdavPath: Optional[str] = Query(None, description="Часть пути к файлу WebDAV"),
    mainCategory: Optional[str] = Query(
        None, description="Основная категория контента"
    ),
    subCategory: Optional[str] = Query(None, description="Подкатегория контента"),
    filePathId: Optional[str] = Query(
        None, description="ID файла для фильтрации блоков"
    ),
    q: Optional[str] = Query(None, description="Полнотекстовый поиск"),
    sortBy: str = Query("orderInFile", description="Поле для сортировки"),
    sortOrder: str = Query("asc", description="Порядок сортировки"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    content_service: ContentService = Depends(get_content_service),
):
    """Получение списка блоков контента с пагинацией и фильтрацией"""

    user_id = current_user.id if current_user else None

    blocks, total = await content_service.get_content_blocks(
        page=page,
        limit=limit,
        webdav_path=webdavPath,
        main_category=mainCategory,
        sub_category=subCategory,
        file_path_id=filePathId,
        search_query=q,
        sort_by=sortBy,
        sort_order=sortOrder,
        user_id=user_id,
    )

    # Обрабатываем текстовый контент
    for block in blocks:
        if hasattr(block, "textContent"):
            block.textContent = unescape_text_content(block.textContent)

    return ContentBlocksListResponse.create(blocks, page, limit, total)


@router.get("/files", response_model=ContentFilesListResponse)
async def get_content_files(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=100, description="Количество файлов на странице"),
    mainCategory: Optional[str] = Query(None, description="Основная категория"),
    subCategory: Optional[str] = Query(None, description="Подкатегория"),
    webdavPath: Optional[str] = Query(None, description="Поиск по пути WebDAV"),
    content_service: ContentService = Depends(get_content_service),
):
    """Получение списка файлов контента с пагинацией"""

    files, total = await content_service.get_content_files(
        page=page,
        limit=limit,
        main_category=mainCategory,
        sub_category=subCategory,
        webdav_path=webdavPath,
    )

    return ContentFilesListResponse.create(files, page, limit, total)


@router.get("/categories", response_model=ContentCategoriesResponse)
async def get_content_categories(
    content_service: ContentService = Depends(get_content_service),
):
    """Получение списка категорий контента"""

    categories = await content_service.get_content_categories()

    return ContentCategoriesResponse.create(categories)


@router.get(
    "/categories/{category}/subcategories", response_model=ContentSubcategoriesResponse
)
async def get_content_subcategories(
    category: str, content_service: ContentService = Depends(get_content_service)
):
    """Получение списка подкатегорий для указанной категории"""

    subcategories = await content_service.get_content_subcategories(category)

    return ContentSubcategoriesResponse.create(subcategories)


@router.get("/blocks/{block_id}", response_model=ContentBlockResponse)
async def get_content_block(
    block_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    content_service: ContentService = Depends(get_content_service),
):
    """Получение блока контента по ID"""

    user_id = current_user.id if current_user else None

    block = await content_service.get_content_block_by_id(block_id, user_id)

    # Обрабатываем текстовый контент
    if hasattr(block, "textContent"):
        block.textContent = unescape_text_content(block.textContent)

    return block


@router.patch("/blocks/{block_id}/progress", response_model=UserContentProgressResponse)
async def update_content_block_progress(
    block_id: str,
    action_data: ProgressAction,
    current_user: User = Depends(get_current_user_required),
    content_service: ContentService = Depends(get_content_service),
):
    """Обновление прогресса пользователя по блоку"""

    progress = await content_service.update_content_block_progress(
        block_id=block_id, user_id=current_user.id, action=action_data
    )

    return UserContentProgressResponse.from_orm(progress)
