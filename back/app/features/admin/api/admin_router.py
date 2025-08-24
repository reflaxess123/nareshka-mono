"""Admin API роутер"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.shared.database import get_session

router = APIRouter(tags=["admin"])


@router.get("/stats")
async def get_admin_stats(session: Session = Depends(get_session)):
    """Получить статистику для админ панели"""
    try:
        # Подсчет пользователей
        from app.shared.models.user_models import User

        total_users = session.query(User).count()
        admin_users = session.query(User).filter(User.role == "ADMIN").count()
        regular_users = session.query(User).filter(User.role == "USER").count()
        guest_users = session.query(User).filter(User.role == "GUEST").count()

        # Подсчет контента
        from app.shared.entities.content import ContentBlock, ContentFile
        from app.shared.models.theory_models import TheoryCard

        total_files = session.query(ContentFile).count()
        total_blocks = session.query(ContentBlock).count()
        total_theory_cards = session.query(TheoryCard).count()

        # Подсчет прогресса
        from app.shared.models.content_models import UserContentProgress
        from app.shared.models.theory_models import UserTheoryProgress

        total_content_progress = session.query(UserContentProgress).count()
        total_theory_progress = session.query(UserTheoryProgress).count()

        return {
            "users": {
                "total": total_users,
                "admins": admin_users,
                "regularUsers": regular_users,
                "guests": guest_users,
            },
            "content": {
                "totalFiles": total_files,
                "totalBlocks": total_blocks,
                "totalTheoryCards": total_theory_cards,
            },
            "progress": {
                "totalContentProgress": total_content_progress,
                "totalTheoryProgress": total_theory_progress,
            },
        }
    except Exception as e:
        return {
            "users": {"total": 0, "admins": 0, "regularUsers": 0, "guests": 0},
            "content": {"totalFiles": 0, "totalBlocks": 0, "totalTheoryCards": 0},
            "progress": {"totalContentProgress": 0, "totalTheoryProgress": 0},
            "error": str(e),
        }
