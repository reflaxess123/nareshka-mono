"""
Interviews API Router
Endpoints для работы с интервью - повторяет паттерн content_router.py
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.features.interviews.dto.categories_responses import CompanyResponse
from app.features.interviews.dto.responses import (
    AnalyticsResponse,
    CompaniesListResponse,
    CompaniesListWithCountResponse,
    CompanyStatsResponse,
    CompanyWithCountResponse,
    InterviewDetailResponse,
    InterviewsListResponse,
)
from app.features.interviews.services.categories_service import CategoriesService
from app.features.interviews.services.interview_service import InterviewService
from app.shared.database import get_session
from app.shared.dependencies import get_current_user_optional

router = APIRouter(
    prefix="/interviews",
    tags=["interviews"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/",
    response_model=InterviewsListResponse,
    summary="Получить список интервью",
    description="Возвращает список интервью с поддержкой фильтрации по компании и пагинации",
)
def get_interviews(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(20, ge=1, le=100, description="Количество записей на странице"),
    company: Optional[str] = Query(
        None, description="Фильтр по названию компании (устарел, используйте companies)"
    ),
    companies: Optional[List[str]] = Query(
        None, description="Фильтр по списку компаний"
    ),
    search: Optional[str] = Query(None, description="Поиск по содержимому интервью"),
    has_audio: Optional[bool] = Query(
        None, description="Фильтр по наличию аудио/видео записи"
    ),
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user_optional),
):
    """Получение списка интервью с фильтрацией и пагинацией

    - **page**: Номер страницы (начинается с 1)
    - **limit**: Количество записей на странице (максимум 100)
    - **company**: Название компании для фильтрации (устарел)
    - **companies**: Список компаний для фильтрации
    - **search**: Поиск по тексту интервью
    """
    service = InterviewService(session)

    # Поддержка как старого формата (company), так и нового (companies)
    companies_filter = None
    if companies:
        companies_filter = companies
    elif company:
        companies_filter = [company]

    filters = {"companies": companies_filter, "search": search, "has_audio": has_audio}

    return service.get_interviews_list(page=page, limit=limit, filters=filters)


@router.get(
    "/company/{company_name}/stats",
    response_model=CompanyStatsResponse,
    summary="Статистика по компании",
    description="Возвращает подробную статистику по интервью конкретной компании",
)
def get_company_stats(
    company_name: str,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user_optional),
):
    """Статистика по конкретной компании

    Включает:
    - Общее количество интервью
    - Средняя продолжительность
    """
    service = InterviewService(session)
    stats = service.get_company_statistics(company_name)

    if not stats:
        raise HTTPException(status_code=404, detail="Company not found")

    return stats


@router.get(
    "/analytics/overview",
    response_model=AnalyticsResponse,
    summary="Общая аналитика",
    description="Возвращает сводную аналитику по всем интервью в системе",
)
def get_analytics_overview(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user_optional),
):
    """Общая аналитика по всем интервью

    Включает:
    - Общее количество интервью и компаний
    - Топ компании по количеству интервью
    - Статистика по месяцам
    """
    service = InterviewService(session)
    return service.get_analytics_overview()


@router.get(
    "/companies/list",
    response_model=CompaniesListWithCountResponse,
    summary="Список компаний",
    description="Возвращает список всех компаний с количеством вопросов для использования в фильтрах",
)
def get_companies_list(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user_optional),
):
    """Список всех компаний для фильтров

    Возвращает массив компаний с количеством вопросов
    """
    service = InterviewService(session)
    companies_with_count = service.get_companies_with_count()
    result = {"companies": companies_with_count}
    return result




@router.get(
    "/detail/{interview_id}",
    response_model=InterviewDetailResponse,
    summary="Получить детали интервью",
    description="Возвращает полную информацию об интервью включая полный текст",
)
def get_interview_detail(
    interview_id: str,
    session: Session = Depends(get_session),
):
    """Получение детальной информации об интервью

    Возвращает полную информацию об интервью включая:
    - Полный текст интервью
    - Все метаданные
    - Извлеченные URL
    - Технологии и теги
    """
    service = InterviewService(session)
    interview = service.get_interview_by_id(interview_id)

    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    return interview
