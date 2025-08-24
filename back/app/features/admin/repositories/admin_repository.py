"""Admin repository for data access"""

from typing import Dict

from sqlalchemy.orm import Session

from app.features.admin.exceptions import AdminStatsException
from app.shared.models.user_models import User
from app.shared.entities.content import ContentBlock, ContentFile
from app.shared.models.theory_models import TheoryCard
from app.shared.models.content_models import UserContentProgress
from app.shared.models.theory_models import UserTheoryProgress


class AdminRepository:
    """Repository for admin data operations"""

    def __init__(self, session: Session):
        self.session = session

    async def get_user_stats(self) -> Dict[str, int]:
        """Get user statistics"""
        try:
            total_users = self.session.query(User).count()
            admin_users = self.session.query(User).filter(User.role == "ADMIN").count()
            regular_users = self.session.query(User).filter(User.role == "USER").count()
            guest_users = self.session.query(User).filter(User.role == "GUEST").count()

            return {
                "total": total_users,
                "admins": admin_users,
                "regular_users": regular_users,
                "guests": guest_users,
            }
        except Exception as e:
            raise AdminStatsException(f"Failed to get user statistics: {str(e)}")

    async def get_content_stats(self) -> Dict[str, int]:
        """Get content statistics"""
        try:
            total_files = self.session.query(ContentFile).count()
            total_blocks = self.session.query(ContentBlock).count()
            total_theory_cards = self.session.query(TheoryCard).count()

            return {
                "total_files": total_files,
                "total_blocks": total_blocks,
                "total_theory_cards": total_theory_cards,
            }
        except Exception as e:
            raise AdminStatsException(f"Failed to get content statistics: {str(e)}")

    async def get_progress_stats(self) -> Dict[str, int]:
        """Get progress statistics"""
        try:
            total_content_progress = self.session.query(UserContentProgress).count()
            total_theory_progress = self.session.query(UserTheoryProgress).count()

            return {
                "total_content_progress": total_content_progress,
                "total_theory_progress": total_theory_progress,
            }
        except Exception as e:
            raise AdminStatsException(f"Failed to get progress statistics: {str(e)}")

    async def get_system_stats(self) -> Dict[str, int]:
        """Get system statistics"""
        import psutil

        return {
            "uptime_seconds": int(psutil.boot_time()),
            "memory_usage_mb": psutil.virtual_memory().used / 1024 / 1024,
            "database_connections": self._get_db_connections_count(),
        }

    async def get_users_list(self, page: int = 1, limit: int = 10) -> Dict:
        """Get paginated list of users"""
        try:
            offset = (page - 1) * limit
            users = self.session.query(User).offset(offset).limit(limit).all()
            total = self.session.query(User).count()
            
            return {
                "items": users,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "totalPages": (total + limit - 1) // limit,
                }
            }
        except Exception as e:
            raise AdminStatsException(f"Failed to get users list: {str(e)}")

    def _get_db_connections_count(self) -> int:
        """Get active database connections count"""
        try:
            result = self.session.execute(
                "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
            )
            return result.scalar() or 0
        except Exception:
            return 0