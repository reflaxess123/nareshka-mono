"""Admin API роутер"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.features.admin.dto.responses import AdminStatsResponse, UsersListResponse
from app.features.admin.services.admin_service import AdminService
from app.features.admin.api.decorators import require_admin
from app.shared.database import get_session
from app.shared.dependencies import get_current_admin_session
from app.shared.models.user_models import User

router = APIRouter(tags=["admin"])


@require_admin
@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(
    current_admin: User = Depends(get_current_admin_session),
    session: Session = Depends(get_session),
) -> AdminStatsResponse:
    """Получить статистику для админ панели"""
    admin_service = AdminService(session)
    return await admin_service.get_admin_stats()


@require_admin
@router.get("/users", response_model=UsersListResponse)
async def get_users(
    page: int = 1,
    limit: int = 10,
    current_admin: User = Depends(get_current_admin_session),
    session: Session = Depends(get_session),
) -> UsersListResponse:
    """Получить список пользователей"""
    admin_service = AdminService(session)
    return await admin_service.get_users_list(page, limit)
