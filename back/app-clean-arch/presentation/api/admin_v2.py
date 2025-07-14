"""Admin API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.status import HTTP_404_NOT_FOUND

from app.application.dto.admin_dto import (
    AdminContentBlockResponse,
    AdminContentFileResponse,
    AdminTheoryCardResponse,
    AdminUserResponse,
    BulkDeleteRequest,
    BulkDeleteResponse,
    ContentStatsResponse,
    CreateContentBlockRequest,
    CreateContentFileRequest,
    CreateTheoryCardRequest,
    CreateUserRequest,
    HealthResponse,
    PaginatedContentBlocksResponse,
    PaginatedContentFilesResponse,
    PaginatedTheoryCardsResponse,
    PaginatedUsersResponse,
    SystemStatsResponse,
    UpdateContentBlockRequest,
    UpdateContentFileRequest,
    UpdateTheoryCardRequest,
    UpdateUserRequest,
    UserStatsResponse,
)
from app.application.services.admin_service import AdminService
from app.core.exceptions import NotFoundException
from app.shared.dependencies import get_admin_service

router = APIRouter(tags=["Admin"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Проверка здоровья Admin модуля"""
    return HealthResponse(status="healthy", module="admin")


@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    admin_service: AdminService = Depends(get_admin_service),
):
    """Получение системной статистики"""
    stats = await admin_service.get_system_stats()
    return SystemStatsResponse(
        users=stats.users, content=stats.content, progress=stats.progress
    )


@router.get("/users", response_model=PaginatedUsersResponse)
async def get_users(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(
        20, ge=1, le=100, description="Количество пользователей на странице"
    ),
    role: Optional[str] = Query(None, description="Фильтр по роли"),
    search: Optional[str] = Query(None, description="Поиск по email"),
    admin_service: AdminService = Depends(get_admin_service),
):
    """Получение списка пользователей"""
    skip = (page - 1) * limit
    users, total = await admin_service.get_users_with_stats(
        skip=skip, limit=limit, role=role, search=search
    )

    user_responses = [
        UserStatsResponse(
            id=user.id,
            email=user.email,
            role=user.role,
            createdAt=user.created_at,
            updatedAt=user.updated_at,
            _count={
                "progress": user.content_progress_count,
                "theoryProgress": user.theory_progress_count,
            },
        )
        for user in users
    ]

    return PaginatedUsersResponse.create(
        items=user_responses, page=page, limit=limit, total=total
    )


@router.post("/users", response_model=AdminUserResponse)
async def create_user(
    user_data: CreateUserRequest,
    admin_service: AdminService = Depends(get_admin_service),
):
    """Создание нового пользователя"""
    user = await admin_service.create_user(
        email=user_data.email, password=user_data.password, role=user_data.role
    )
    return AdminUserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        createdAt=user.created_at,
        updatedAt=user.updated_at,
        _count={
            "progress": 0,  # Новый пользователь не имеет прогресса
            "theoryProgress": 0,
        },
    )


@router.put("/users/{user_id}", response_model=AdminUserResponse)
async def update_user(
    user_id: str,
    user_data: UpdateUserRequest,
    admin_service: AdminService = Depends(get_admin_service),
):
    """Обновление пользователя"""
    user = await admin_service.update_user(
        user_id=user_id,
        email=user_data.email,
        password=user_data.password,
        role=user_data.role,
    )

    if not user:
        raise NotFoundException("User", user_id)

    return AdminUserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        createdAt=user.created_at,
        updatedAt=user.updated_at,
        _count={
            "progress": 0,  # Обновляем без подсчета прогресса для упрощения
            "theoryProgress": 0,
        },
    )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin_service: AdminService = Depends(get_admin_service),
):
    """Удаление пользователя"""
    deleted = await admin_service.delete_user(user_id)
    if not deleted:
        raise NotFoundException("User", user_id)

    return {"message": "Пользователь успешно удален"}


@router.get("/content/stats", response_model=ContentStatsResponse)
async def get_content_stats(
    admin_service: AdminService = Depends(get_admin_service),
):
    """Получение статистики контента"""
    stats = await admin_service.get_content_stats()
    return ContentStatsResponse(
        total_files=stats.total_files,
        total_blocks=stats.total_blocks,
        files_by_category=stats.files_by_category,
        blocks_by_category=stats.blocks_by_category,
    )


@router.get("/content/files", response_model=PaginatedContentFilesResponse)
async def get_content_files(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    admin_service: AdminService = Depends(get_admin_service),
):
    """Получение списка файлов контента"""
    skip = (page - 1) * limit
    files, total = await admin_service.get_content_files(
        skip=skip, limit=limit, category=category, search=search
    )

    return PaginatedContentFilesResponse(
        files=[
            AdminContentFileResponse(
                id=file.id,
                webdav_path=file.webdav_path,
                main_category=file.main_category,
                sub_category=file.sub_category,
                created_at=file.created_at,
                updated_at=file.updated_at,
                _count={"blocks": file.blocks_count},
            )
            for file in files
        ],
        total=total,
        page=page,
        limit=limit,
        totalPages=(total + limit - 1) // limit if limit > 0 else 0,
    )


@router.post("/content/files", response_model=AdminContentFileResponse)
async def create_content_file(
    file_data: CreateContentFileRequest,
    admin_service: AdminService = Depends(get_admin_service),
):
    """Создание нового файла контента"""
    try:
        file = await admin_service.create_content_file(
            webdav_path=file_data.webdav_path,
            main_category=file_data.main_category,
            sub_category=file_data.sub_category,
        )
        return AdminContentFileResponse(
            id=file.id,
            webdav_path=file.webdav_path,
            main_category=file.main_category,
            sub_category=file.sub_category,
            created_at=file.created_at,
            updated_at=file.updated_at,
            _count={"blocks": file.blocks_count},
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.put("/content/files/{file_id}", response_model=AdminContentFileResponse)
async def update_content_file(
    file_id: str,
    file_data: UpdateContentFileRequest,
    admin_service: AdminService = Depends(get_admin_service),
):
    """Обновление файла контента"""
    try:
        file = await admin_service.update_content_file(
            file_id=file_id,
            webdav_path=file_data.webdav_path,
            main_category=file_data.main_category,
            sub_category=file_data.sub_category,
        )

        if not file:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Файл не найден")

        return AdminContentFileResponse(
            id=file.id,
            webdav_path=file.webdav_path,
            main_category=file.main_category,
            sub_category=file.sub_category,
            created_at=file.created_at,
            updated_at=file.updated_at,
            _count={"blocks": file.blocks_count},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/content/files/{file_id}")
async def delete_content_file(
    file_id: str,
    admin_service: AdminService = Depends(get_admin_service),
):
    """Удаление файла контента"""
    try:
        deleted = await admin_service.delete_content_file(file_id)
        if not deleted:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Файл не найден")

        return {"message": "Файл успешно удален"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/content/blocks", response_model=PaginatedContentBlocksResponse)
async def get_content_blocks(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    file_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    admin_service: AdminService = Depends(get_admin_service),
):
    """Получение списка блоков контента"""
    try:
        skip = (page - 1) * limit
        blocks, total = await admin_service.get_content_blocks(
            skip=skip, limit=limit, file_id=file_id, search=search
        )

        return PaginatedContentBlocksResponse(
            blocks=[
                AdminContentBlockResponse(
                    id=block.id,
                    file_id=block.file_id,
                    block_title=block.block_title,
                    block_level=block.block_level,
                    order_in_file=block.order_in_file,
                    text_content=block.text_content,
                    code_content=block.code_content,
                    code_language=block.code_language,
                    is_code_foldable=block.is_code_foldable,
                    _count={"testCases": block.test_cases_count},
                )
                for block in blocks
            ],
            total=total,
            page=page,
            limit=limit,
            totalPages=(total + limit - 1) // limit if limit > 0 else 0,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/content/blocks", response_model=AdminContentBlockResponse)
async def create_content_block(
    block_data: CreateContentBlockRequest,
    admin_service: AdminService = Depends(get_admin_service),
):
    """Создание нового блока контента"""
    try:
        block = await admin_service.create_content_block(
            file_id=block_data.file_id,
            block_title=block_data.block_title,
            block_level=block_data.block_level,
            order_in_file=block_data.order_in_file,
            text_content=block_data.text_content,
            code_content=block_data.code_content,
            code_language=block_data.code_language,
            is_code_foldable=block_data.is_code_foldable,
        )
        return AdminContentBlockResponse(
            id=block.id,
            file_id=block.file_id,
            block_title=block.block_title,
            block_level=block.block_level,
            order_in_file=block.order_in_file,
            text_content=block.text_content,
            code_content=block.code_content,
            code_language=block.code_language,
            is_code_foldable=block.is_code_foldable,
            _count={"testCases": block.test_cases_count},
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.put("/content/blocks/{block_id}", response_model=AdminContentBlockResponse)
async def update_content_block(
    block_id: str,
    block_data: UpdateContentBlockRequest,
    admin_service: AdminService = Depends(get_admin_service),
):
    """Обновление блока контента"""
    try:
        block = await admin_service.update_content_block(
            block_id=block_id,
            file_id=block_data.file_id,
            block_title=block_data.block_title,
            block_level=block_data.block_level,
            order_in_file=block_data.order_in_file,
            text_content=block_data.text_content,
            code_content=block_data.code_content,
            code_language=block_data.code_language,
            is_code_foldable=block_data.is_code_foldable,
        )

        if not block:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Блок не найден")

        return AdminContentBlockResponse(
            id=block.id,
            file_id=block.file_id,
            block_title=block.block_title,
            block_level=block.block_level,
            order_in_file=block.order_in_file,
            text_content=block.text_content,
            code_content=block.code_content,
            code_language=block.code_language,
            is_code_foldable=block.is_code_foldable,
            _count={"testCases": block.test_cases_count},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/content/blocks/{block_id}")
async def delete_content_block(
    block_id: str,
    admin_service: AdminService = Depends(get_admin_service),
):
    """Удаление блока контента"""
    try:
        deleted = await admin_service.delete_content_block(block_id)
        if not deleted:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Блок не найден")

        return {"message": "Блок успешно удален"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/theory/cards", response_model=PaginatedTheoryCardsResponse)
async def get_theory_cards(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    admin_service: AdminService = Depends(get_admin_service),
):
    """Получение списка теоретических карточек"""
    try:
        skip = (page - 1) * limit
        cards, total = await admin_service.get_theory_cards(
            skip=skip, limit=limit, category=category, search=search
        )

        return PaginatedTheoryCardsResponse(
            cards=[
                AdminTheoryCardResponse(
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
                )
                for card in cards
            ],
            total=total,
            page=page,
            limit=limit,
            totalPages=(total + limit - 1) // limit if limit > 0 else 0,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/theory/cards", response_model=AdminTheoryCardResponse)
async def create_theory_card(
    card_data: CreateTheoryCardRequest,
    admin_service: AdminService = Depends(get_admin_service),
):
    """Создание новой теоретической карточки"""
    try:
        card = await admin_service.create_theory_card(
            anki_guid=card_data.anki_guid,
            card_type=card_data.card_type,
            deck=card_data.deck,
            category=card_data.category,
            sub_category=card_data.sub_category,
            question_block=card_data.question_block,
            answer_block=card_data.answer_block,
            tags=card_data.tags,
            order_index=card_data.order_index,
        )
        return AdminTheoryCardResponse(
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
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.put("/theory/cards/{card_id}", response_model=AdminTheoryCardResponse)
async def update_theory_card(
    card_id: str,
    card_data: UpdateTheoryCardRequest,
    admin_service: AdminService = Depends(get_admin_service),
):
    """Обновление теоретической карточки"""
    try:
        card = await admin_service.update_theory_card(
            card_id=card_id,
            anki_guid=card_data.anki_guid,
            card_type=card_data.card_type,
            deck=card_data.deck,
            category=card_data.category,
            sub_category=card_data.sub_category,
            question_block=card_data.question_block,
            answer_block=card_data.answer_block,
            tags=card_data.tags,
            order_index=card_data.order_index,
        )

        if not card:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Карточка не найдена"
            )

        return AdminTheoryCardResponse(
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
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/theory/cards/{card_id}")
async def delete_theory_card(
    card_id: str,
    admin_service: AdminService = Depends(get_admin_service),
):
    """Удаление теоретической карточки"""
    try:
        deleted = await admin_service.delete_theory_card(card_id)
        if not deleted:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Карточка не найдена"
            )

        return {"message": "Карточка успешно удалена"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/content/bulk-delete", response_model=BulkDeleteResponse)
async def bulk_delete_content(
    delete_data: BulkDeleteRequest,
    admin_service: AdminService = Depends(get_admin_service),
):
    """Массовое удаление контента"""
    try:
        result = await admin_service.bulk_delete_content(delete_data.ids)
        return BulkDeleteResponse(
            deleted_count=result.deleted_count, failed_count=result.failed_count
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/theory/bulk-delete", response_model=BulkDeleteResponse)
async def bulk_delete_theory(
    delete_data: BulkDeleteRequest,
    admin_service: AdminService = Depends(get_admin_service),
):
    """Массовое удаление теоретических карточек"""
    try:
        result = await admin_service.bulk_delete_theory(delete_data.ids)
        return BulkDeleteResponse(
            deleted_count=result.deleted_count, failed_count=result.failed_count
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
