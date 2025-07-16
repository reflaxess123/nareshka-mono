"""Сервис для работы с теоретическими карточками"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple

from app.shared.entities.enums import CardState
from app.features.theory.repositories.theory_repository import TheoryRepository
from app.features.theory.exceptions.theory_exceptions import (
    TheoryCardNotFoundError,
    InvalidProgressActionError,
    InvalidReviewRatingError,
    TheoryProgressError,
)
from app.features.theory.dto.requests import ProgressAction, ReviewRating
from app.features.theory.dto.responses import (
    TheoryCardResponse,
    TheoryCardWithProgressResponse,
    TheoryCategoriesResponse,
    TheoryStatsResponse,
    UserTheoryProgressResponse,
    DueCardsResponse,
)

logger = logging.getLogger(__name__)


class TheoryService:
    """Сервис для работы с теоретическими карточками"""

    def __init__(self, theory_repository: TheoryRepository):
        self.theory_repository = theory_repository

    def _calculate_next_review(
        self, progress, rating: str
    ) -> Tuple[int, Decimal, CardState, int]:
        """Алгоритм интервального повторения (SuperMemo SM-2)"""
        
        current_ease = progress.easeFactor
        current_interval = progress.interval
        current_state = progress.cardState
        learning_step = progress.learningStep

        # Обработка оценки
        if rating == "again":
            quality = 1
        elif rating == "hard":
            quality = 2
        elif rating == "good":
            quality = 3
        elif rating == "easy":
            quality = 4
        else:
            raise InvalidReviewRatingError(rating)

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

        # Карточка на повторении
        elif current_state == CardState.REVIEW:
            if quality < 3:
                new_state = CardState.LEARNING
                new_interval = 1
                new_step = 0
                new_ease = max(1.3, current_ease - 0.2)
            else:
                new_state = CardState.REVIEW
                new_step = 0
                
                if quality == 3:
                    new_interval = max(1, int(current_interval * current_ease))
                    new_ease = current_ease
                elif quality == 2:
                    new_interval = max(1, int(current_interval * 1.2))
                    new_ease = max(1.3, current_ease - 0.15)
                else:  # quality == 4
                    new_interval = max(1, int(current_interval * current_ease * 1.3))
                    new_ease = current_ease + 0.15

        else:
            # Fallback для неизвестного состояния
            new_state = CardState.NEW
            new_interval = 1
            new_ease = Decimal("2.5")
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
        user_id: Optional[int] = None,
    ) -> Tuple[List[TheoryCardResponse], int]:
        """Получение теоретических карточек с пагинацией и фильтрацией"""
        logger.info(f"Получение карточек: page={page}, limit={limit}, category={category}")
        
        try:
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
                user_id=user_id,
            )

            # Преобразование в DTO
            card_responses = []
            for card in cards:
                card_response = TheoryCardResponse.model_validate(card)
                logger.info(f"Card response dump: {card_response.model_dump()}")
                card_responses.append(card_response)

            logger.info(f"Найдено {total} карточек, возвращено {len(card_responses)}")
            return card_responses, total
        
        except Exception as e:
            logger.error(f"Ошибка при получении карточек: {str(e)}")
            raise

    async def get_theory_card_by_id(
        self, card_id: str, user_id: Optional[int] = None
    ) -> TheoryCardResponse:
        """Получение карточки по ID"""
        logger.info(f"Получение карточки {card_id}")
        
        card = await self.theory_repository.get_theory_card_by_id(card_id)
        if not card:
            raise TheoryCardNotFoundError(card_id)

        # Если указан пользователь, добавляем прогресс
        if user_id:
            progress = await self.theory_repository.get_user_theory_progress(user_id, card_id)
            if progress:
                return TheoryCardWithProgressResponse(
                    **card.__dict__,
                    progress=UserTheoryProgressResponse.model_validate(progress)
                )

        return TheoryCardResponse.model_validate(card)

    async def get_theory_categories(self) -> TheoryCategoriesResponse:
        """Получение списка категорий"""
        logger.info("Получение категорий теории")
        
        categories = await self.theory_repository.get_theory_categories()
        return TheoryCategoriesResponse(categories=categories)

    async def get_theory_subcategories(self, category: str) -> List[str]:
        """Получение подкатегорий"""
        logger.info(f"Получение подкатегорий для категории {category}")
        
        return await self.theory_repository.get_theory_subcategories(category)

    async def update_theory_card_progress(
        self, card_id: str, user_id: int, action: ProgressAction
    ) -> UserTheoryProgressResponse:
        """Обновление прогресса изучения карточки"""
        logger.info(f"Обновление прогресса карточки {card_id} для пользователя {user_id}: {action.action}")
        
        # Проверяем корректность действия
        if action.action not in ["increment", "decrement"]:
            raise InvalidProgressActionError(action.action)

        # Получаем или создаём прогресс
        progress = await self.theory_repository.get_user_theory_progress(user_id, card_id)
        
        if not progress:
            # Создаём начальный прогресс
            if action.action == "increment":
                progress_data = {"solvedCount": 1}
            else:
                progress_data = {"solvedCount": 0}
                
            progress = await self.theory_repository.create_or_update_user_progress(
                user_id, card_id, **progress_data
            )
        else:
            # Обновляем существующий прогресс
            if action.action == "increment":
                new_count = progress.solvedCount + 1
            else:
                new_count = max(0, progress.solvedCount - 1)
                
            progress = await self.theory_repository.create_or_update_user_progress(
                user_id, card_id, solvedCount=new_count
            )

        logger.info(f"Прогресс обновлён: solvedCount={progress.solvedCount}")
        return UserTheoryProgressResponse.model_validate(progress)

    async def review_theory_card(
        self, card_id: str, user_id: int, review: ReviewRating
    ) -> UserTheoryProgressResponse:
        """Повторение карточки с алгоритмом интервального повторения"""
        logger.info(f"Повторение карточки {card_id} пользователем {user_id}: {review.rating}")
        
        # Получаем или создаём прогресс
        progress = await self.theory_repository.get_user_theory_progress(user_id, card_id)
        
        if not progress:
            # Создаём начальный прогресс для новой карточки
            progress = await self.theory_repository.create_or_update_user_progress(
                user_id, card_id,
                solvedCount=0,
                easeFactor=Decimal("2.5"),
                interval=1,
                reviewCount=0,
                lapseCount=0,
                cardState=CardState.NEW,
                learningStep=0,
            )

        # Вычисляем новые параметры
        new_interval, new_ease, new_state, new_step = self._calculate_next_review(
            progress, review.rating
        )

        # Обновляем прогресс
        current_time = datetime.utcnow()
        due_date = current_time + timedelta(minutes=new_interval)
        
        update_data = {
            "interval": new_interval,
            "easeFactor": new_ease,
            "cardState": new_state,
            "learningStep": new_step,
            "dueDate": due_date,
            "lastReviewDate": current_time,
            "reviewCount": progress.reviewCount + 1,
            "solvedCount": progress.solvedCount + 1,
        }
        
        # Увеличиваем количество ошибок при неудачном ответе
        if review.rating in ["again", "hard"]:
            update_data["lapseCount"] = progress.lapseCount + 1

        progress = await self.theory_repository.create_or_update_user_progress(
            user_id, card_id, **update_data
        )

        logger.info(f"Карточка {card_id} повторена: state={new_state}, interval={new_interval}")
        return UserTheoryProgressResponse.model_validate(progress)

    async def get_due_theory_cards(
        self, user_id: int, limit: int = 10
    ) -> DueCardsResponse:
        """Получение карточек для повторения"""
        logger.info(f"Получение карточек для повторения пользователя {user_id}")
        
        cards = await self.theory_repository.get_due_theory_cards(user_id, limit)
        card_responses = [TheoryCardResponse.model_validate(card) for card in cards]
        
        logger.info(f"Найдено {len(card_responses)} карточек для повторения")
        return DueCardsResponse(cards=card_responses, total=len(card_responses))

    async def get_theory_stats(self, user_id: int) -> TheoryStatsResponse:
        """Получение статистики изучения"""
        logger.info(f"Получение статистики теории для пользователя {user_id}")
        
        stats = await self.theory_repository.get_theory_stats(user_id)
        return TheoryStatsResponse(**stats)

    async def reset_card_progress(self, card_id: str, user_id: int) -> bool:
        """Сброс прогресса по карточке"""
        logger.info(f"Сброс прогресса карточки {card_id} для пользователя {user_id}")
        
        success = await self.theory_repository.reset_card_progress(user_id, card_id)
        
        if success:
            logger.info(f"Прогресс карточки {card_id} сброшен")
        else:
            logger.warning(f"Не удалось сбросить прогресс карточки {card_id}")
            
        return success 


