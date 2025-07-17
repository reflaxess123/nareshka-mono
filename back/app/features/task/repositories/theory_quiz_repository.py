"""Репозиторий для работы с теоретическими тестами"""

from typing import List, Optional, Tuple
from sqlalchemy import asc, func, or_
from sqlalchemy.orm import Session, joinedload

from app.shared.entities.task_types import Task
from app.shared.models.theory_models import TheoryCard, UserTheoryProgress

import logging

logger = logging.getLogger(__name__)


class TheoryQuizRepository:
    """Репозиторий для работы с теоретическими тестами"""

    def __init__(self, session: Session):
        self.session = session

    def get_theory_quizzes(
        self,
        user_id: Optional[int] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Tuple[List[Task], int]:
        """Получить теоретические тесты с фильтрацией"""
        
        # Базовый запрос для теоретических карточек
        query = (
            self.session.query(TheoryCard)
            .filter(TheoryCard.is_deleted == False)
        )

        # Фильтрация по категории
        if category:
            query = query.filter(TheoryCard.category == category)

        # Поиск по вопросу
        if search:
            search_filter = TheoryCard.question.ilike(f"%{search}%")
            query = query.filter(search_filter)

        # Подсчет общего количества
        total_count = query.count()

        # Применение пагинации
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        # Сортировка по id (можно изменить при необходимости)
        query = query.order_by(asc(TheoryCard.id))

        theory_cards = query.all()

        # Получение прогресса пользователя для теоретических карточек
        user_progress = {}
        if user_id:
            progress_query = (
                self.session.query(UserTheoryProgress)
                .filter(UserTheoryProgress.user_id == user_id)
                .filter(
                    UserTheoryProgress.theory_card_id.in_(
                        [tc.id for tc in theory_cards]
                    )
                )
            )
            user_progress_records = progress_query.all()
            user_progress = {
                up.theory_card_id: up for up in user_progress_records
            }

        # Преобразование в объекты Task
        tasks = []
        for card in theory_cards:
            progress = user_progress.get(card.id)

            task = Task(
                id=card.id,
                title=f"Теория: {card.question[:50]}...",  # Ограничиваем длину заголовка
                content=card.question,
                category=card.category,
                company=None,  # У теоретических карточек нет компании
                language=None,  # У теоретических карточек нет языка
                difficulty=card.difficulty,
                type="theory_quiz",
                order_in_file=None,  # У теоретических карточек нет порядка в файле
                files=[],  # У теоретических карточек нет файлов
                is_completed=progress.is_completed if progress else False,
                progress_percentage=progress.progress_percentage if progress else 0,
                time_spent=progress.time_spent if progress else 0,
                last_viewed=progress.last_viewed if progress else None,
                attempts_count=progress.attempts_count if progress else 0,
                # Дополнительные поля для теоретических тестов
                question=card.question,
                answer_options=card.answer_options if hasattr(card, 'answer_options') else [],
                correct_answer=card.correct_answer if hasattr(card, 'correct_answer') else None,
                explanation=card.explanation if hasattr(card, 'explanation') else None,
            )
            tasks.append(task)

        return tasks, total_count

    def get_theory_quiz_categories(self) -> List[str]:
        """Получить список уникальных категорий теоретических тестов"""
        categories = (
            self.session.query(TheoryCard.category)
            .filter(TheoryCard.is_deleted == False)
            .filter(TheoryCard.category.isnot(None))
            .distinct()
            .all()
        )
        return [cat[0] for cat in categories if cat[0]]

    def get_theory_quiz_by_id(self, quiz_id: int) -> Optional[TheoryCard]:
        """Получить теоретический тест по ID"""
        return (
            self.session.query(TheoryCard)
            .filter(TheoryCard.id == quiz_id)
            .filter(TheoryCard.is_deleted == False)
            .first()
        )