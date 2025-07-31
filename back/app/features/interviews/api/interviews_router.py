"""
Interviews API Router
Endpoints для работы с интервью - повторяет паттерн content_router.py
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.features.interviews.services.interview_service import InterviewService
from app.features.interviews.dto.responses import (
    InterviewsListResponse,
    InterviewDetailResponse, 
    AnalyticsResponse,
    CompanyStatsResponse,
    CompaniesListResponse,
    TechnologiesListResponse
)
from app.shared.dependencies import get_current_user_optional
from app.shared.database import get_session

router = APIRouter(
    prefix="/interviews", 
    tags=["interviews"],
    responses={404: {"description": "Not found"}}
)


@router.get(
    "/", 
    response_model=InterviewsListResponse,
    summary="Получить список интервью",
    description="Возвращает список интервью с поддержкой фильтрации по компании, технологиям, сложности и пагинации"
)
async def get_interviews(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(20, ge=1, le=100, description="Количество записей на странице"),
    company: Optional[str] = Query(None, description="Фильтр по названию компании"),
    technology: Optional[str] = Query(None, description="Фильтр по технологии"),
    difficulty: Optional[int] = Query(None, ge=1, le=5, description="Фильтр по сложности (1-5)"),
    stage: Optional[int] = Query(None, ge=1, le=4, description="Фильтр по этапу собеседования (1-4)"),
    search: Optional[str] = Query(None, description="Поиск по содержимому интервью"),
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user_optional)
):
    """Получение списка интервью с фильтрацией и пагинацией
    
    - **page**: Номер страницы (начинается с 1)
    - **limit**: Количество записей на странице (максимум 100)
    - **company**: Название компании для фильтрации
    - **technology**: Технология для фильтрации  
    - **difficulty**: Уровень сложности от 1 до 5
    - **stage**: Этап собеседования от 1 до 4
    - **search**: Поиск по тексту интервью
    """
    service = InterviewService(session)
    
    filters = {
        "company": company,
        "technology": technology, 
        "difficulty": difficulty,
        "stage": stage,
        "search": search
    }
    
    return service.get_interviews_list(
        page=page,
        limit=limit,
        filters=filters
    )


@router.get(
    "/{interview_id}", 
    response_model=InterviewDetailResponse,
    summary="Получить детали интервью",
    description="Возвращает полную информацию об интервью включая полный текст"
)
async def get_interview_detail(
    interview_id: str,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user_optional)
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


@router.get(
    "/company/{company_name}/stats", 
    response_model=CompanyStatsResponse,
    summary="Статистика по компании",
    description="Возвращает подробную статистику по интервью конкретной компании"
)
async def get_company_stats(
    company_name: str,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user_optional)
):
    """Статистика по конкретной компании
    
    Включает:
    - Общее количество интервью
    - Средняя сложность
    - Средняя продолжительность
    - Популярные технологии
    - Распределение по этапам
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
    description="Возвращает сводную аналитику по всем интервью в системе"
)
async def get_analytics_overview(
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user_optional)
):
    """Общая аналитика по всем интервью
    
    Включает:
    - Общее количество интервью и компаний
    - Топ компании по количеству интервью
    - Популярные технологии
    - Распределение по сложности
    - Статистика по месяцам
    """
    service = InterviewService(session)
    return service.get_analytics_overview()


@router.get(
    "/companies/list",
    response_model=CompaniesListResponse,
    summary="Список компаний",
    description="Возвращает список всех компаний для использования в фильтрах"
)
async def get_companies_list(
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user_optional)
):
    """Список всех компаний для фильтров
    
    Возвращает массив названий компаний, присутствующих в базе данных интервью
    """
    service = InterviewService(session)
    return {"companies": service.get_companies_list()}


@router.get(
    "/technologies/list",
    response_model=TechnologiesListResponse,
    summary="Список технологий", 
    description="Возвращает список всех технологий для использования в фильтрах"
)
async def get_technologies_list(
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user_optional)
):
    """Список всех технологий для фильтров
    
    Возвращает массив технологий, упоминаемых в интервью
    """
    service = InterviewService(session)
    return {"technologies": service.get_technologies_list()}