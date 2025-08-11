"""
Companies API Router - отдельный роутер для работы с компаниями
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.shared.database import get_session
from app.shared.dependencies import get_current_user_optional
from app.features.interviews.services.categories_service import CategoriesService
from app.features.interviews.dto.categories_responses import CompanyResponse


router = APIRouter(
    prefix="/companies",
    tags=["companies"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)


@router.get(
    "/top",
    response_model=List[CompanyResponse],
    summary="Получить топ компаний",
    description="Возвращает список компаний с наибольшим количеством вопросов"
)
def get_top_companies(
    limit: int = Query(
        20, 
        ge=1, 
        le=100, 
        description="Количество компаний в топе"
    ),
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user_optional)
) -> List[CompanyResponse]:
    """
    Получить топ компаний по количеству вопросов
    
    Возвращает список компаний, отсортированный по убыванию количества
    вопросов от каждой компании.
    """
    service = CategoriesService(session)
    return service.get_top_companies(limit=limit)