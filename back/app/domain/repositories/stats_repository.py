from abc import ABC, abstractmethod
from typing import Dict, List, Any

from ..entities.stats_types import (
    UserStatsOverview,
    ContentStats,
    TheoryStats,
    RoadmapStats
)


class StatsRepository(ABC):
    """Repository для работы со статистикой"""
    
    @abstractmethod
    async def get_user_stats_overview(self, user_id: int) -> UserStatsOverview:
        """Получение общей статистики пользователя"""
        pass
    
    @abstractmethod
    async def get_content_stats(self, user_id: int) -> ContentStats:
        """Получение детальной статистики по контенту"""
        pass
    
    @abstractmethod
    async def get_theory_stats(self, user_id: int) -> TheoryStats:
        """Получение детальной статистики по теории"""
        pass
    
    @abstractmethod
    async def get_roadmap_stats(self, user_id: int) -> RoadmapStats:
        """Получение roadmap статистики по категориям"""
        pass
    
    # Вспомогательные методы для статистики
    @abstractmethod
    async def get_content_blocks_with_progress(self, user_id: int) -> List[Any]:
        """Получение блоков контента с прогрессом пользователя"""
        pass
    
    @abstractmethod
    async def get_theory_cards_with_progress(self, user_id: int) -> List[Any]:
        """Получение карточек теории с прогрессом пользователя"""
        pass
    
    @abstractmethod
    async def get_content_categories(self) -> List[tuple]:
        """Получение всех категорий контента"""
        pass
    
    @abstractmethod
    async def get_theory_categories(self) -> List[tuple]:
        """Получение всех категорий теории"""
        pass
    
    @abstractmethod
    async def get_content_blocks_by_category(self, category: str) -> List[Any]:
        """Получение блоков контента по категории"""
        pass
    
    @abstractmethod
    async def get_theory_cards_by_category(self, category: str) -> List[Any]:
        """Получение карточек теории по категории"""
        pass
    
    @abstractmethod
    async def get_user_content_progress_for_blocks(self, user_id: int, block_ids: List[str]) -> List[Any]:
        """Получение прогресса пользователя по блокам контента"""
        pass
    
    @abstractmethod
    async def get_user_theory_progress_for_cards(self, user_id: int, card_ids: List[str]) -> List[Any]:
        """Получение прогресса пользователя по карточкам теории"""
        pass 