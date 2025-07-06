"""Интерфейс репозитория для работы с теоретическими карточками"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from ..entities.theory import TheoryCard, UserTheoryProgress


class TheoryRepository(ABC):
    """Абстрактный репозиторий для работы с теоретическими карточками"""
    
    @abstractmethod
    async def get_theory_cards(
        self,
        page: int = 1,
        limit: int = 10,
        category: Optional[str] = None,
        sub_category: Optional[str] = None,
        deck: Optional[str] = None,
        search_query: Optional[str] = None,
        sort_by: str = "orderIndex",
        sort_order: str = "asc",
        only_unstudied: bool = False,
        user_id: Optional[int] = None
    ) -> Tuple[List[TheoryCard], int]:
        """Получение теоретических карточек с пагинацией и фильтрацией"""
        pass
    
    @abstractmethod
    async def get_theory_card_by_id(self, card_id: str) -> Optional[TheoryCard]:
        """Получение теоретической карточки по ID"""
        pass
    
    @abstractmethod
    async def get_theory_categories(self) -> List[Dict[str, Any]]:
        """Получение списка категорий с подкатегориями и количеством карточек"""
        pass
    
    @abstractmethod
    async def get_theory_subcategories(self, category: str) -> List[str]:
        """Получение списка подкатегорий для категории"""
        pass
    
    @abstractmethod
    async def get_user_theory_progress(
        self, 
        user_id: int, 
        card_id: str
    ) -> Optional[UserTheoryProgress]:
        """Получение прогресса пользователя по карточке"""
        pass
    
    @abstractmethod
    async def create_or_update_user_progress(
        self,
        user_id: int,
        card_id: str,
        **progress_data
    ) -> UserTheoryProgress:
        """Создание или обновление прогресса пользователя"""
        pass
    
    @abstractmethod
    async def get_due_theory_cards(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[TheoryCard]:
        """Получение карточек для повторения"""
        pass
    
    @abstractmethod
    async def get_theory_stats(self, user_id: int) -> Dict[str, Any]:
        """Получение статистики изучения теории пользователя"""
        pass
    
    @abstractmethod
    async def reset_card_progress(self, user_id: int, card_id: str) -> bool:
        """Сброс прогресса по карточке"""
        pass 