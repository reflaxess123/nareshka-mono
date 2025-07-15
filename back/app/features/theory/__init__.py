"""
Theory Feature - теоретические карточки для изучения.

Этот модуль содержит всю логику для работы с теоретическими карточками:
- Карточки теории (TheoryCard)
- Прогресс пользователя по карточкам (UserTheoryProgress)
- Spaced Repetition алгоритм для повторения
"""

from app.shared.models.theory_models import (
    TheoryCard,
    UserTheoryProgress,
)
from app.features.theory.services.theory_service import TheoryService
from app.features.theory.repositories.theory_repository import TheoryRepository
# Router импортируется напрямую в main.py для избежания циклических импортов

__all__ = [
    # Models
    "TheoryCard",
    "UserTheoryProgress",
    # Services
    "TheoryService",
    # Repositories
    "TheoryRepository",
] 



