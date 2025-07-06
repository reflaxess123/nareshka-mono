"""Сервис для работы с теоретическими карточками"""

from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import HTTPException, status

from ...domain.entities.theory import TheoryCard, UserTheoryProgress
from ...domain.entities.enums import CardState
from ...domain.repositories.theory_repository import TheoryRepository
from ..dto.theory_dto import (
    TheoryCardResponse,
    TheoryCardWithProgressResponse,
    UserTheoryProgressResponse,
    ProgressAction,
    ReviewRating,
    TheoryCategoriesResponse,
    TheoryStatsResponse
)


class TheoryService:
    """Сервис для работы с теоретическими карточками"""
    
    def __init__(self, theory_repository: TheoryRepository):
        self.theory_repository = theory_repository
    
    def _calculate_next_review(
        self, 
        progress: UserTheoryProgress, 
        rating: str
    ) -> Tuple[int, Decimal, CardState, int]:
        """Алгоритм интервального повторения (SuperMemo SM-2)"""
        
        current_ease = progress.easeFactor
        current_interval = progress.interval
        current_state = progress.cardState
        learning_step = progress.learningStep
        
        # Обработка оценки
        if rating == "again":  # 1
            quality = 1
        elif rating == "hard":  # 2
            quality = 2
        elif rating == "good":  # 3
            quality = 3
        elif rating == "easy":  # 4
            quality = 4
        else:
            quality = 3  # по умолчанию
        
        # Новая карточка
        if current_state == CardState.NEW:
            if quality >= 3:
                new_state = CardState.LEARNING
                new_interval = 1
                new_ease = current_ease
                new_step = 0
            else:
                new_state = CardState.LEARNING
                new_interval = 1
                new_ease = current_ease
                new_step = 0
        
        # Изучаемая карточка
        elif current_state == CardState.LEARNING:
            if quality >= 3:
                if learning_step == 0:
                    new_interval = 6
                    new_step = 1
                    new_state = CardState.LEARNING
                else:
                    new_interval = 1
                    new_step = 0
                    new_state = CardState.REVIEW
                new_ease = current_ease
            else:
                new_interval = 1
                new_step = 0
                new_state = CardState.LEARNING
                new_ease = current_ease
        
        # Повторяемая карточка
        elif current_state == CardState.REVIEW:
            if quality >= 3:
                new_state = CardState.REVIEW
                new_step = 0
                
                # Пересчет ease factor
                new_ease = max(
                    Decimal("1.30"),
                    current_ease + Decimal("0.1") - (5 - quality) * (Decimal("0.08") + (5 - quality) * Decimal("0.02"))
                )
                
                # Новый интервал
                if quality == 3:
                    new_interval = max(1, int(current_interval * new_ease))
                else:  # quality == 4
                    new_interval = max(1, int(current_interval * new_ease * Decimal("1.3")))
            else:
                new_state = CardState.RELEARNING
                new_interval = 1
                new_step = 0
                new_ease = max(Decimal("1.30"), current_ease - Decimal("0.20"))
        
        # Переизучаемая карточка
        elif current_state == CardState.RELEARNING:
            if quality >= 3:
                new_state = CardState.REVIEW
                new_interval = max(1, current_interval)
                new_step = 0
                new_ease = current_ease
            else:
                new_state = CardState.RELEARNING
                new_interval = 1
                new_step = 0
                new_ease = current_ease
        else:
            # Значения по умолчанию
            new_interval = 1
            new_ease = current_ease
            new_state = CardState.LEARNING
            new_step = 0
        
        return new_interval, new_ease, new_state, new_step
    
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
    ) -> Tuple[List[TheoryCardResponse], int]:
        """Получение теоретических карточек с пагинацией и фильтрацией"""
        cards, total = await self.theory_repository.get_theory_cards(
            page=page,
            limit=limit,
            category=category,
            sub_category=sub_category,
            deck=deck,
            search_query=search_query,
            sort_by=sort_by,
            sort_order=sort_order,
            only_unstudied=only_unstudied,
            user_id=user_id
        )
        
        # Если пользователь аутентифицирован, добавляем прогресс
        if user_id:
            card_responses = []
            for card in cards:
                progress = await self.theory_repository.get_user_theory_progress(
                    user_id, card.id
                )
                card_response = TheoryCardWithProgressResponse.from_orm(card)
                if progress:
                    card_response.progress = UserTheoryProgressResponse.from_orm(progress)
                else:
                    card_response.progress = None
                card_responses.append(card_response)
            return card_responses, total
        else:
            return [TheoryCardResponse.from_orm(card) for card in cards], total
    
    async def get_theory_card_by_id(
        self, 
        card_id: str, 
        user_id: Optional[int] = None
    ) -> TheoryCardResponse:
        """Получение теоретической карточки по ID"""
        card = await self.theory_repository.get_theory_card_by_id(card_id)
        
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Theory card not found"
            )
        
        if user_id:
            progress = await self.theory_repository.get_user_theory_progress(
                user_id, card_id
            )
            card_response = TheoryCardWithProgressResponse.from_orm(card)
            if progress:
                card_response.progress = UserTheoryProgressResponse.from_orm(progress)
            else:
                card_response.progress = None
            return card_response
        else:
            return TheoryCardResponse.from_orm(card)
    
    async def get_theory_categories(self) -> TheoryCategoriesResponse:
        """Получение списка категорий теоретических карточек"""
        categories = await self.theory_repository.get_theory_categories()
        return TheoryCategoriesResponse(categories=categories)
    
    async def get_theory_subcategories(self, category: str) -> List[str]:
        """Получение списка подкатегорий для категории"""
        return await self.theory_repository.get_theory_subcategories(category)
    
    async def update_theory_card_progress(
        self,
        card_id: str,
        user_id: int,
        action: ProgressAction
    ) -> UserTheoryProgress:
        """Обновление прогресса пользователя по карточке"""
        # Проверяем существование карточки
        card = await self.theory_repository.get_theory_card_by_id(card_id)
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Theory card not found"
            )
        
        # Получаем текущий прогресс
        current_progress = await self.theory_repository.get_user_theory_progress(
            user_id, card_id
        )
        current_count = current_progress.solvedCount if current_progress else 0
        
        # Обновляем счетчик
        if action.action == "increment":
            new_count = current_count + 1
        elif action.action == "decrement":
            new_count = max(0, current_count - 1)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid action. Use 'increment' or 'decrement'"
            )
        
        # Сохраняем новый прогресс
        return await self.theory_repository.create_or_update_user_progress(
            user_id=user_id,
            card_id=card_id,
            solvedCount=new_count
        )
    
    async def review_theory_card(
        self,
        card_id: str,
        user_id: int,
        review: ReviewRating
    ) -> UserTheoryProgress:
        """Проведение повторения карточки с оценкой"""
        # Проверяем существование карточки
        card = await self.theory_repository.get_theory_card_by_id(card_id)
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Theory card not found"
            )
        
        # Получаем или создаем прогресс
        progress = await self.theory_repository.get_user_theory_progress(user_id, card_id)
        
        if not progress:
            # Создаем новый прогресс
            progress = await self.theory_repository.create_or_update_user_progress(
                user_id=user_id,
                card_id=card_id,
                solvedCount=0,
                easeFactor=Decimal("2.50"),
                interval=1,
                reviewCount=0,
                lapseCount=0,
                cardState=CardState.NEW,
                learningStep=0
            )
        
        # Вычисляем следующий интервал
        new_interval, new_ease, new_state, new_step = self._calculate_next_review(
            progress, review.rating
        )
        
        # Обновляем прогресс
        now = datetime.utcnow()
        update_data = {
            "solvedCount": progress.solvedCount + 1,
            "easeFactor": new_ease,
            "interval": new_interval,
            "dueDate": now + timedelta(days=new_interval),
            "reviewCount": progress.reviewCount + 1,
            "cardState": new_state,
            "learningStep": new_step,
            "lastReviewDate": now
        }
        
        # Увеличиваем счетчик неудач для плохих оценок
        if review.rating in ["again", "hard"]:
            update_data["lapseCount"] = progress.lapseCount + 1
        
        return await self.theory_repository.create_or_update_user_progress(
            user_id=user_id,
            card_id=card_id,
            **update_data
        )
    
    async def get_due_theory_cards(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[TheoryCardResponse]:
        """Получение карточек для повторения"""
        cards = await self.theory_repository.get_due_theory_cards(user_id, limit)
        return [TheoryCardResponse.from_orm(card) for card in cards]
    
    async def get_theory_stats(self, user_id: int) -> TheoryStatsResponse:
        """Получение статистики изучения теории пользователя"""
        stats = await self.theory_repository.get_theory_stats(user_id)
        return TheoryStatsResponse(**stats)
    
    async def reset_card_progress(self, card_id: str, user_id: int) -> bool:
        """Сброс прогресса по карточке"""
        # Проверяем существование карточки
        card = await self.theory_repository.get_theory_card_by_id(card_id)
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Theory card not found"
            )
        
        return await self.theory_repository.reset_card_progress(user_id, card_id) 