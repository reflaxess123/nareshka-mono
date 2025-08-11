"""
Categories API Router - роутер для работы с категориями вопросов
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, HTTPException
from sqlalchemy.orm import Session

from app.shared.database import get_session
from app.shared.dependencies import get_current_user_optional
from app.features.interviews.services.categories_service import CategoriesService
from app.features.interviews.dto.categories_responses import (
    CategoryResponse,
    CategoryDetailResponse,
    QuestionResponse,
    QuestionsListResponse,
    CategoriesStatisticsResponse,
    CompanyResponse
)
from app.features.interviews.exceptions.interview_exceptions import (
    CategoryNotFoundError,
    ClusterNotFoundError
)


router = APIRouter(
    prefix="/interview-categories",
    tags=["interview-categories"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)


@router.get(
    "/",
    response_model=List[CategoryResponse],
    summary="Получить список категорий",
    description="Возвращает все категории вопросов интервью с статистикой"
)
def get_categories(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user_optional)
) -> List[CategoryResponse]:
    """
    Получить все категории вопросов
    
    Возвращает список всех категорий с информацией о количестве вопросов,
    кластеров и процентном соотношении.
    """
    service = CategoriesService(session)
    return service.get_all_categories()


@router.get(
    "/statistics",
    response_model=CategoriesStatisticsResponse,
    summary="Получить статистику категоризации",
    description="Возвращает общую статистику по категоризации вопросов"
)
def get_statistics(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user_optional)
) -> CategoriesStatisticsResponse:
    """
    Получить общую статистику
    
    Возвращает информацию о количестве вопросов, категорий,
    кластеров и проценте категоризации.
    """
    service = CategoriesService(session)
    return service.get_statistics()


@router.get(
    "/cluster/{cluster_id}/questions",
    response_model=List[QuestionResponse],
    summary="Получить вопросы кластера",
    description="Возвращает список вопросов определенного кластера"
)
def get_cluster_questions(
    cluster_id: int = Path(..., description="ID кластера"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(
        50, 
        ge=1, 
        le=200, 
        description="Количество вопросов на странице"
    ),
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user_optional)
) -> List[QuestionResponse]:
    """
    Получить вопросы определенного кластера
    
    Возвращает список всех вопросов, относящихся к указанному кластеру,
    с поддержкой пагинации.
    """
    service = CategoriesService(session)
    
    try:
        return service.get_cluster_questions(
            cluster_id=cluster_id,
            page=page,
            limit=limit
        )
    except ClusterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/search/questions",
    response_model=QuestionsListResponse,
    summary="Поиск вопросов",
    description="Полнотекстовый поиск по вопросам интервью с фильтрацией и пагинацией"
)
def search_questions(
    q: str = Query(
        ..., 
        min_length=1, 
        description="Поисковый запрос (минимум 1 символ, * для всех)"
    ),
    category_id: Optional[str] = Query(
        None, 
        description="Фильтр по ID категории"
    ),
    company: Optional[str] = Query(
        None, 
        description="Фильтр по названию компании"
    ),
    limit: int = Query(
        50, 
        ge=1, 
        le=500, 
        description="Максимальное количество результатов"
    ),
    offset: int = Query(
        0, 
        ge=0, 
        description="Смещение для пагинации"
    ),
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user_optional)
) -> QuestionsListResponse:
    """
    Поиск вопросов по тексту
    
    Выполняет полнотекстовый поиск по вопросам с возможностью фильтрации
    по категории и компании.
    """
    service = CategoriesService(session)
    
    return service.search_questions(
        search_query=q,
        category_id=category_id,
        company=company,
        limit=limit,
        offset=offset
    )



@router.get(
    "/companies/top",
    response_model=List[CompanyResponse],
    summary="Получить топ компаний",
    description="Возвращает список компаний с наибольшим количеством вопросов"
)
def get_top_companies_endpoint(
    limit: int = Query(
        20, 
        ge=1, 
        le=100, 
        description="Количество компаний в топе"
    ),
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user_optional)
) -> List[CompanyResponse]:
    service = CategoriesService(session)
    return service.get_top_companies(limit=limit)


@router.get(
    "/companies/count",
    response_model=int,
    summary="Получить общее количество компаний",
    description="Возвращает общее количество уникальных компаний в базе данных"
)
def get_total_companies_count(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user_optional)
) -> int:
    service = CategoriesService(session)
    return service.get_total_companies_count()


@router.get(
    "/{category_id}",
    response_model=CategoryDetailResponse,
    summary="Получить детали категории",
    description="Возвращает подробную информацию о категории с кластерами и примерами"
)
def get_category_detail(
    category_id: str = Path(..., description="ID категории (например: javascript_core)"),
    limit_questions: int = Query(
        10, 
        ge=1, 
        le=50, 
        description="Количество примеров вопросов"
    ),
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user_optional)
) -> CategoryDetailResponse:
    """
    Получить детальную информацию о категории
    
    Возвращает полную информацию о категории, включая:
    - Основную информацию о категории
    - Список всех кластеров категории
    - Примеры вопросов из категории
    """
    service = CategoriesService(session)
    
    try:
        return service.get_category_detail(
            category_id=category_id,
            limit_questions=limit_questions
        )
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))