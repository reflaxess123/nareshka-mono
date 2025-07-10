"""API endpoints для работы с теоретическими карточками"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.dto.theory_dto import (
    DueCardsResponse,
    ProgressAction,
    ReviewRating,
    TheoryCardResponse,
    TheoryCardsListResponse,
    TheoryCategoriesResponse,
    TheoryStatsResponse,
    TheorySubcategoriesResponse,
    UserTheoryProgressResponse,
)
from app.application.services.theory_service import TheoryService
from app.shared.dependencies import (
    get_current_user_optional,
    get_current_user_required,
    get_theory_service,
)

router = APIRouter(prefix="/theory", tags=["Theory v2"])


@router.get("/cards", response_model=TheoryCardsListResponse)
async def get_theory_cards(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=100, description="Количество карточек на странице"),
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    subCategory: Optional[str] = Query(None, description="Фильтр по подкатегории"),
    deck: Optional[str] = Query(None, description="Поиск по названию колоды"),
    sortBy: str = Query("orderIndex", description="Поле для сортировки"),
    sortOrder: str = Query("asc", description="Порядок сортировки"),
    q: Optional[str] = Query(None, description="Полнотекстовый поиск"),
    onlyUnstudied: bool = Query(
        False, description="Показывать только неизученные карточки"
    ),
    current_user=Depends(get_current_user_optional),
    theory_service: TheoryService = Depends(get_theory_service),
):
    """Получение списка теоретических карточек с пагинацией и фильтрацией"""
    user_id = current_user.id if current_user else None

    cards, total = await theory_service.get_theory_cards(
        page=page,
        limit=limit,
        category=category,
        sub_category=subCategory,
        deck=deck,
        search_query=q,
        sort_by=sortBy,
        sort_order=sortOrder,
        only_unstudied=onlyUnstudied,
        user_id=user_id,
    )

    return TheoryCardsListResponse.create(cards, total, page, limit)


@router.get("/categories", response_model=TheoryCategoriesResponse)
async def get_theory_categories(
    theory_service: TheoryService = Depends(get_theory_service),
):
    """Получение списка всех категорий теории"""
    return await theory_service.get_theory_categories()


@router.get(
    "/categories/{category}/subcategories", response_model=TheorySubcategoriesResponse
)
async def get_theory_subcategories(
    category: str, theory_service: TheoryService = Depends(get_theory_service)
):
    """Получение списка подкатегорий для категории"""
    subcategories = await theory_service.get_theory_subcategories(category)
    return TheorySubcategoriesResponse(subcategories=subcategories)


@router.get("/cards/{card_id}", response_model=TheoryCardResponse)
async def get_theory_card(
    card_id: str,
    current_user=Depends(get_current_user_optional),
    theory_service: TheoryService = Depends(get_theory_service),
):
    """Получение теоретической карточки по ID"""
    user_id = current_user.id if current_user else None
    return await theory_service.get_theory_card_by_id(card_id, user_id)


@router.patch("/cards/{card_id}/progress", response_model=UserTheoryProgressResponse)
async def update_theory_card_progress(
    card_id: str,
    action_data: ProgressAction,
    current_user=Depends(get_current_user_required),
    theory_service: TheoryService = Depends(get_theory_service),
):
    """Обновление прогресса изучения карточки"""
    progress = await theory_service.update_theory_card_progress(
        card_id=card_id, user_id=current_user.id, action=action_data
    )
    return UserTheoryProgressResponse.from_orm(progress)


@router.post("/cards/{card_id}/review", response_model=UserTheoryProgressResponse)
async def review_theory_card(
    card_id: str,
    review_data: ReviewRating,
    current_user=Depends(get_current_user_required),
    theory_service: TheoryService = Depends(get_theory_service),
):
    """Проведение повторения карточки с оценкой"""
    progress = await theory_service.review_theory_card(
        card_id=card_id, user_id=current_user.id, review=review_data
    )
    return UserTheoryProgressResponse.from_orm(progress)


@router.get("/cards/due", response_model=DueCardsResponse)
async def get_due_theory_cards(
    limit: int = Query(10, ge=1, le=100, description="Количество карточек"),
    current_user=Depends(get_current_user_required),
    theory_service: TheoryService = Depends(get_theory_service),
):
    """Получение карточек для повторения"""
    cards = await theory_service.get_due_theory_cards(
        user_id=current_user.id, limit=limit
    )
    return DueCardsResponse(cards=cards, total=len(cards))


@router.get("/stats", response_model=TheoryStatsResponse)
async def get_theory_stats_overview(
    current_user=Depends(get_current_user_required),
    theory_service: TheoryService = Depends(get_theory_service),
):
    """Получение общей статистики изучения теории пользователя"""
    return await theory_service.get_theory_stats(current_user.id)


@router.post("/cards/{card_id}/reset")
async def reset_theory_card_progress(
    card_id: str,
    current_user=Depends(get_current_user_required),
    theory_service: TheoryService = Depends(get_theory_service),
):
    """Сброс прогресса по карточке"""
    success = await theory_service.reset_card_progress(
        card_id=card_id, user_id=current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Progress not found"
        )

    return {"message": "Progress reset successfully"}
