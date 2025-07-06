"""API для работы с контентом (новая архитектура)"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request

from ...application.services.content_service import ContentService
from ...application.dto.content_dto import (
    ContentBlocksListResponse,
    ContentFilesListResponse,
    ContentBlockResponse,
    ContentCategoriesResponse,
    ContentSubcategoriesResponse,
    ProgressAction,
    UserContentProgressResponse
)
from ...domain.repositories.unit_of_work import UnitOfWork
from ...domain.entities.user import User
from ...shared.dependencies import get_unit_of_work, get_current_user_optional, get_current_user_required

router = APIRouter(prefix="/content", tags=["content"])


def unescape_text_content(text: Optional[str]) -> Optional[str]:
    """Заменяет экранированные символы на настоящие переносы строк"""
    if not text:
        return text
    return text.replace("\\n", "\n").replace("\\t", "\t")


async def get_content_service(uow: UnitOfWork = Depends(get_unit_of_work)) -> ContentService:
    """Получение сервиса контента"""
    async with uow:
        return ContentService(uow.content)


@router.get("/blocks", response_model=ContentBlocksListResponse)
async def get_content_blocks(
    request: Request,
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=100, description="Количество блоков на странице"),
    webdavPath: Optional[str] = Query(None, description="Часть пути к файлу WebDAV"),
    mainCategory: Optional[str] = Query(None, description="Основная категория контента"),
    subCategory: Optional[str] = Query(None, description="Подкатегория контента"),
    filePathId: Optional[str] = Query(None, description="ID файла для фильтрации блоков"),
    q: Optional[str] = Query(None, description="Полнотекстовый поиск"),
    sortBy: str = Query("orderInFile", description="Поле для сортировки"),
    sortOrder: str = Query("asc", description="Порядок сортировки"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    uow: UnitOfWork = Depends(get_unit_of_work)
):
    """Получение списка блоков контента с пагинацией и фильтрацией"""
    
    user_id = current_user.id if current_user else None
    
    async with uow:
        content_service = ContentService(uow.content)
        
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
            user_id=user_id
        )
        
        # Обрабатываем текстовый контент
        for block in blocks:
            if hasattr(block, 'textContent'):
                block.textContent = unescape_text_content(block.textContent)
        
        return ContentBlocksListResponse.create(blocks, total, page, limit)


@router.get("/files", response_model=ContentFilesListResponse)
async def get_content_files(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=100, description="Количество файлов на странице"),
    mainCategory: Optional[str] = Query(None, description="Основная категория"),
    subCategory: Optional[str] = Query(None, description="Подкатегория"),
    webdavPath: Optional[str] = Query(None, description="Поиск по пути WebDAV"),
    uow: UnitOfWork = Depends(get_unit_of_work)
):
    """Получение списка файлов контента с пагинацией"""
    
    async with uow:
        content_service = ContentService(uow.content)
        
        files, total = await content_service.get_content_files(
            page=page,
            limit=limit,
            main_category=mainCategory,
            sub_category=subCategory,
            webdav_path=webdavPath
        )
        
        return ContentFilesListResponse.create(files, total, page, limit)


@router.get("/categories", response_model=ContentCategoriesResponse)
async def get_content_categories(uow: UnitOfWork = Depends(get_unit_of_work)):
    """Получение списка категорий контента"""
    
    async with uow:
        content_service = ContentService(uow.content)
        categories = await content_service.get_content_categories()
        
        return ContentCategoriesResponse(categories=categories)


@router.get("/categories/{category}/subcategories", response_model=ContentSubcategoriesResponse)
async def get_content_subcategories(
    category: str,
    uow: UnitOfWork = Depends(get_unit_of_work)
):
    """Получение списка подкатегорий для указанной категории"""
    
    async with uow:
        content_service = ContentService(uow.content)
        subcategories = await content_service.get_content_subcategories(category)
        
        return ContentSubcategoriesResponse(subcategories=subcategories)


@router.get("/blocks/{block_id}", response_model=ContentBlockResponse)
async def get_content_block(
    block_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    uow: UnitOfWork = Depends(get_unit_of_work)
):
    """Получение блока контента по ID"""
    
    user_id = current_user.id if current_user else None
    
    async with uow:
        content_service = ContentService(uow.content)
        block = await content_service.get_content_block_by_id(block_id, user_id)
        
        # Обрабатываем текстовый контент
        if hasattr(block, 'textContent'):
            block.textContent = unescape_text_content(block.textContent)
        
        return block


@router.patch("/blocks/{block_id}/progress", response_model=UserContentProgressResponse)
async def update_content_block_progress(
    block_id: str,
    action_data: ProgressAction,
    current_user: User = Depends(get_current_user_required),
    uow: UnitOfWork = Depends(get_unit_of_work)
):
    """Обновление прогресса пользователя по блоку"""
    
    async with uow:
        content_service = ContentService(uow.content)
        progress = await content_service.update_content_block_progress(
            block_id=block_id,
            user_id=current_user.id,
            action=action_data
        )
        
        await uow.commit()
        
        return UserContentProgressResponse.from_orm(progress) 