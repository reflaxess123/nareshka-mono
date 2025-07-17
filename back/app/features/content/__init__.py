"""
Content Feature - образовательный контент платформы.

Этот модуль содержит всю логику для работы с образовательным контентом:
- Файлы контента (ContentFile)
- Блоки контента (ContentBlock) 
- Прогресс пользователя по контенту (UserContentProgress)
"""

from app.shared.entities.content import ContentFile, ContentBlock
from app.features.content.services.content_service import ContentService
from app.features.content.repositories.content_repository import ContentRepository
__all__ = [
    # Models
    "ContentFile",
    "ContentBlock", 
    "ContentBlockProgress",
    # Services
    "ContentService",
    # Repositories
    "ContentRepository",
] 



