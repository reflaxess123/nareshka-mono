"""Admin service for business logic"""

from typing import Optional

from sqlalchemy.orm import Session

from app.features.admin.dto.responses import (
    AdminStatsResponse,
    ContentStatsResponse,
    ProgressStatsResponse,
    SystemStatsResponse,
    UsersListResponse,
    UserStatsResponse,
)
from app.features.auth.dto.responses import UserResponse
from app.features.admin.repositories.admin_repository import AdminRepository
from app.features.admin.exceptions import AdminStatsException


class AdminService:
    """Service for admin operations"""

    def __init__(self, session: Session):
        self.repository = AdminRepository(session)

    async def get_admin_stats(self) -> AdminStatsResponse:
        """Get complete admin dashboard statistics"""
        try:
            user_stats = await self._get_user_stats()
            content_stats = await self._get_content_stats()
            progress_stats = await self._get_progress_stats()
            system_stats = await self._get_system_stats()

            return AdminStatsResponse(
                users=user_stats,
                content=content_stats,
                progress=progress_stats,
                system=system_stats,
            )
        except Exception as e:
            raise AdminStatsException(f"Failed to retrieve admin statistics: {str(e)}")

    async def _get_user_stats(self) -> UserStatsResponse:
        """Get user statistics"""
        stats = await self.repository.get_user_stats()
        return UserStatsResponse(
            total=stats["total"],
            admins=stats["admins"],
            regularUsers=stats["regular_users"],
            guests=stats["guests"],
        )

    async def _get_content_stats(self) -> ContentStatsResponse:
        """Get content statistics"""
        stats = await self.repository.get_content_stats()
        return ContentStatsResponse(
            totalFiles=stats["total_files"],
            totalBlocks=stats["total_blocks"],
            totalTheoryCards=stats["total_theory_cards"],
        )

    async def _get_progress_stats(self) -> ProgressStatsResponse:
        """Get progress statistics"""
        stats = await self.repository.get_progress_stats()
        return ProgressStatsResponse(
            totalContentProgress=stats["total_content_progress"],
            totalTheoryProgress=stats["total_theory_progress"],
        )

    async def _get_system_stats(self) -> Optional[SystemStatsResponse]:
        """Get system statistics"""
        try:
            stats = await self.repository.get_system_stats()
            return SystemStatsResponse(
                uptimeSeconds=stats.get("uptime_seconds"),
                memoryUsageMB=stats.get("memory_usage_mb"),
                databaseConnections=stats.get("database_connections"),
            )
        except Exception:
            return None

    async def get_users_list(self, page: int = 1, limit: int = 10) -> UsersListResponse:
        """Get paginated list of users"""
        data = await self.repository.get_users_list(page, limit)
        
        users = [UserResponse.from_user(user) for user in data["items"]]
        
        return UsersListResponse(
            items=users,
            pagination=data["pagination"],
        )