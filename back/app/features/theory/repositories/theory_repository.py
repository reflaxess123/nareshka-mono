"""Репозиторий для работы с теоретическими карточками"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from sqlalchemy import and_, asc, desc, func, or_
from sqlalchemy.orm import Session

from app.features.theory.exceptions.theory_exceptions import (
    TheoryCardNotFoundError,
    TheoryProgressError,
)
from app.shared.entities.enums import CardState
from app.shared.models.theory_models import (
    TheoryCard,
    UserTheoryProgress,
)


class TheoryRepository:
    """Репозиторий для работы с теоретическими карточками"""

    def __init__(self, session: Session):
        self.session = session

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
    ) -> Tuple[List[TheoryCard], int]:
        """Получение теоретических карточек с пагинацией и фильтрацией"""
        offset = (page - 1) * limit

        query = self.session.query(TheoryCard).filter(
            ~TheoryCard.category.ilike("%QUIZ%"),
            ~TheoryCard.category.ilike("%ПРАКТИКА%"),
        )

        # Фильтры
        if category:
            query = query.filter(
                func.lower(TheoryCard.category) == func.lower(category)
            )

        if sub_category:
            query = query.filter(
                func.lower(TheoryCard.subCategory) == func.lower(sub_category)
            )

        if deck:
            query = query.filter(TheoryCard.deck.ilike(f"%{deck}%"))

        # Поиск
        if search_query and search_query.strip():
            search_term = f"%{search_query.strip()}%"
            query = query.filter(
                or_(
                    TheoryCard.questionBlock.ilike(search_term),
                    TheoryCard.answerBlock.ilike(search_term),
                    TheoryCard.category.ilike(search_term),
                    TheoryCard.subCategory.ilike(search_term),
                )
            )

        # Фильтр неизученных карточек
        if only_unstudied and user_id:
            studied_card_ids = (
                self.session.query(UserTheoryProgress.cardId)
                .filter(
                    UserTheoryProgress.userId == user_id,
                    UserTheoryProgress.solvedCount > 0,
                )
                .subquery()
            )
            query = query.filter(~TheoryCard.id.in_(studied_card_ids))

        # Подсчёт общего количества
        total = query.count()

        # Сортировка
        if hasattr(TheoryCard, sort_by):
            if sort_order.lower() == "desc":
                query = query.order_by(desc(getattr(TheoryCard, sort_by)))
            else:
                query = query.order_by(asc(getattr(TheoryCard, sort_by)))

        # Пагинация
        cards = query.offset(offset).limit(limit).all()

        return cards, total

    async def get_theory_card_by_id(self, card_id: str) -> Optional[TheoryCard]:
        """Получение теоретической карточки по ID"""
        card = self.session.query(TheoryCard).filter(TheoryCard.id == card_id).first()
        return card

    async def get_theory_categories(self) -> List[Dict[str, Any]]:
        """Получение списка категорий с подкатегориями и количеством карточек"""
        categories_data = (
            self.session.query(
                TheoryCard.category,
                TheoryCard.subCategory,
                func.count(TheoryCard.id).label("count"),
            )
            .filter(
                ~TheoryCard.category.ilike("%QUIZ%"),
                ~TheoryCard.category.ilike("%ПРАКТИКА%"),
            )
            .group_by(TheoryCard.category, TheoryCard.subCategory)
            .order_by(TheoryCard.category, TheoryCard.subCategory)
            .all()
        )

        # Группировка по категориям
        categories_dict = {}
        for category, sub_category, count in categories_data:
            if category not in categories_dict:
                categories_dict[category] = {
                    "name": category,
                    "subCategories": [],
                    "totalCards": 0,
                }

            categories_dict[category]["totalCards"] += count

            if sub_category:
                categories_dict[category]["subCategories"].append(
                    {"name": sub_category, "count": count}
                )

        return list(categories_dict.values())

    async def get_theory_subcategories(self, category: str) -> List[str]:
        """Получение списка подкатегорий для категории"""
        subcategories = (
            self.session.query(TheoryCard.subCategory)
            .filter(
                func.lower(TheoryCard.category) == func.lower(category),
                TheoryCard.subCategory.isnot(None),
            )
            .distinct()
            .order_by(TheoryCard.subCategory)
            .all()
        )

        return [sub[0] for sub in subcategories if sub[0]]

    async def get_user_theory_progress(
        self, user_id: int, card_id: str
    ) -> Optional[UserTheoryProgress]:
        """Получение прогресса пользователя по карточке"""
        progress = (
            self.session.query(UserTheoryProgress)
            .filter(
                and_(
                    UserTheoryProgress.userId == user_id,
                    UserTheoryProgress.cardId == card_id,
                )
            )
            .first()
        )
        return progress

    async def create_or_update_user_progress(
        self, user_id: int, card_id: str, **progress_data
    ) -> UserTheoryProgress:
        """Создание или обновление прогресса пользователя"""
        # Проверяем, существует ли карточка
        card = await self.get_theory_card_by_id(card_id)
        if not card:
            raise TheoryCardNotFoundError(card_id)

        progress = await self.get_user_theory_progress(user_id, card_id)

        if progress:
            # Обновляем существующий прогресс
            for key, value in progress_data.items():
                if hasattr(progress, key):
                    setattr(progress, key, value)
            progress.updatedAt = datetime.utcnow()
        else:
            # Создаём новый прогресс
            progress = UserTheoryProgress(
                id=str(uuid4()),
                userId=user_id,
                cardId=card_id,
                createdAt=datetime.utcnow(),
                updatedAt=datetime.utcnow(),
                **progress_data,
            )
            self.session.add(progress)

        try:
            self.session.commit()
            self.session.refresh(progress)
            return progress
        except Exception as e:
            self.session.rollback()
            raise TheoryProgressError(f"Ошибка при сохранении прогресса: {str(e)}")

    async def get_due_theory_cards(
        self, user_id: int, limit: int = 10
    ) -> List[TheoryCard]:
        """Получение карточек, готовых для повторения"""
        current_time = datetime.utcnow()

        # Карточки с истекшим сроком повторения
        due_cards_query = (
            self.session.query(TheoryCard)
            .join(UserTheoryProgress)
            .filter(
                UserTheoryProgress.userId == user_id,
                UserTheoryProgress.dueDate <= current_time,
                UserTheoryProgress.cardState.in_(
                    [CardState.LEARNING, CardState.REVIEW]
                ),
            )
            .order_by(UserTheoryProgress.dueDate)
            .limit(limit)
        )

        # Новые карточки, если недостаточно карточек для повторения
        due_cards = due_cards_query.all()
        remaining_limit = limit - len(due_cards)

        if remaining_limit > 0:
            studied_card_ids = (
                self.session.query(UserTheoryProgress.cardId)
                .filter(UserTheoryProgress.userId == user_id)
                .subquery()
            )

            new_cards = (
                self.session.query(TheoryCard)
                .filter(
                    ~TheoryCard.id.in_(studied_card_ids),
                    ~TheoryCard.category.ilike("%QUIZ%"),
                    ~TheoryCard.category.ilike("%ПРАКТИКА%"),
                )
                .order_by(TheoryCard.orderIndex)
                .limit(remaining_limit)
                .all()
            )

            due_cards.extend(new_cards)

        return due_cards

    async def get_theory_stats(self, user_id: int) -> Dict[str, Any]:
        """Получение статистики изучения теории пользователя"""
        # Общее количество карточек
        total_cards = (
            self.session.query(func.count(TheoryCard.id))
            .filter(
                ~TheoryCard.category.ilike("%QUIZ%"),
                ~TheoryCard.category.ilike("%ПРАКТИКА%"),
            )
            .scalar()
        )

        # Изученные карточки
        studied_cards = (
            self.session.query(func.count(UserTheoryProgress.id))
            .filter(
                UserTheoryProgress.userId == user_id,
                UserTheoryProgress.solvedCount > 0,
            )
            .scalar()
        )

        # Карточки к повторению
        current_time = datetime.utcnow()
        due_cards = (
            self.session.query(func.count(UserTheoryProgress.id))
            .filter(
                UserTheoryProgress.userId == user_id,
                UserTheoryProgress.dueDate <= current_time,
                UserTheoryProgress.cardState.in_(
                    [CardState.LEARNING, CardState.REVIEW]
                ),
            )
            .scalar()
        )

        # Средний фактор лёгкости
        avg_ease_factor = (
            self.session.query(func.avg(UserTheoryProgress.easeFactor))
            .filter(
                UserTheoryProgress.userId == user_id,
                UserTheoryProgress.solvedCount > 0,
            )
            .scalar()
        )

        return {
            "totalCards": total_cards or 0,
            "studiedCards": studied_cards or 0,
            "dueCards": due_cards or 0,
            "averageEaseFactor": float(avg_ease_factor or 2.5),
            "studyProgress": (studied_cards / total_cards * 100)
            if total_cards > 0
            else 0,
        }

    async def reset_card_progress(self, user_id: int, card_id: str) -> bool:
        """Сброс прогресса по карточке"""
        progress = await self.get_user_theory_progress(user_id, card_id)
        if not progress:
            return False

        try:
            self.session.delete(progress)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise TheoryProgressError(f"Ошибка при сбросе прогресса: {str(e)}")
