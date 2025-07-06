"""Реализация репозитория теоретических карточек для SQLAlchemy"""

from typing import List, Optional, Tuple, Dict, Any
from uuid import uuid4
from datetime import datetime
from decimal import Decimal
from sqlalchemy import and_, func, or_, asc, desc
from sqlalchemy.orm import Session

from ...domain.entities.theory import TheoryCard, UserTheoryProgress
from ...domain.entities.enums import CardState
from ...domain.repositories.theory_repository import TheoryRepository


class SQLAlchemyTheoryRepository(TheoryRepository):
    """Реализация репозитория теоретических карточек для SQLAlchemy"""
    
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
        user_id: Optional[int] = None
    ) -> Tuple[List[TheoryCard], int]:
        """Получение теоретических карточек с пагинацией и фильтрацией"""
        offset = (page - 1) * limit
        
        query = self.session.query(TheoryCard).filter(
            ~TheoryCard.category.ilike('%QUIZ%'),
            ~TheoryCard.category.ilike('%ПРАКТИКА%')
        )
        
        # Фильтры
        if category:
            query = query.filter(func.lower(TheoryCard.category) == func.lower(category))
        
        if sub_category:
            query = query.filter(func.lower(TheoryCard.subCategory) == func.lower(sub_category))
        
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
                    TheoryCard.subCategory.ilike(search_term)
                )
            )
        
        # Фильтр неизученных карточек
        if only_unstudied and user_id:
            studied_card_ids = self.session.query(UserTheoryProgress.cardId).filter(
                UserTheoryProgress.userId == user_id,
                UserTheoryProgress.solvedCount > 0
            ).subquery()
            
            query = query.filter(~TheoryCard.id.in_(studied_card_ids))
        
        # Сортировка
        if sort_by == "createdAt":
            order_field = TheoryCard.createdAt
        elif sort_by == "updatedAt":
            order_field = TheoryCard.updatedAt
        elif sort_by == "orderIndex":
            order_field = TheoryCard.orderIndex
        else:
            order_field = TheoryCard.orderIndex
        
        if sort_order == "desc":
            query = query.order_by(desc(order_field))
        else:
            query = query.order_by(asc(order_field))
        
        total = query.count()
        cards = query.offset(offset).limit(limit).all()
        
        return cards, total
    
    async def get_theory_card_by_id(self, card_id: str) -> Optional[TheoryCard]:
        """Получение теоретической карточки по ID"""
        return self.session.query(TheoryCard).filter(TheoryCard.id == card_id).first()
    
    async def get_theory_categories(self) -> List[Dict[str, Any]]:
        """Получение списка категорий с подкатегориями и количеством карточек"""
        categories_data = self.session.query(
            TheoryCard.category,
            TheoryCard.subCategory,
            func.count(TheoryCard.id).label("count")
        ).filter(
            ~TheoryCard.category.ilike('%QUIZ%'),
            ~TheoryCard.category.ilike('%ПРАКТИКА%')
        ).group_by(TheoryCard.category, TheoryCard.subCategory).all()
        
        grouped_categories = {}
        
        for category, sub_category, count in categories_data:
            # Пропускаем тестовые категории
            if category == 'Test' or sub_category == 'Test':
                continue
                
            if category not in grouped_categories:
                grouped_categories[category] = {
                    "name": category,
                    "subCategories": [],
                    "totalCards": 0
                }
            
            if sub_category:
                grouped_categories[category]["subCategories"].append({
                    "name": sub_category,
                    "cardCount": count
                })
            
            grouped_categories[category]["totalCards"] += count
        
        result = []
        for cat_name in sorted(grouped_categories.keys()):
            cat_data = grouped_categories[cat_name]
            cat_data["subCategories"].sort(key=lambda x: x["name"])
            result.append(cat_data)
        
        return result
    
    async def get_theory_subcategories(self, category: str) -> List[str]:
        """Получение списка подкатегорий для категории"""
        return [
            row[0] for row in self.session.query(TheoryCard.subCategory)
            .filter(
                func.lower(TheoryCard.category) == func.lower(category),
                TheoryCard.subCategory.isnot(None)
            )
            .distinct()
            .order_by(TheoryCard.subCategory)
            .all()
        ]
    
    async def get_user_theory_progress(
        self, 
        user_id: int, 
        card_id: str
    ) -> Optional[UserTheoryProgress]:
        """Получение прогресса пользователя по карточке"""
        return self.session.query(UserTheoryProgress).filter(
            and_(
                UserTheoryProgress.userId == user_id,
                UserTheoryProgress.cardId == card_id
            )
        ).first()
    
    async def create_or_update_user_progress(
        self,
        user_id: int,
        card_id: str,
        **progress_data
    ) -> UserTheoryProgress:
        """Создание или обновление прогресса пользователя"""
        progress = await self.get_user_theory_progress(user_id, card_id)
        
        if progress:
            # Обновляем существующий прогресс
            for key, value in progress_data.items():
                if hasattr(progress, key):
                    setattr(progress, key, value)
            progress.updatedAt = datetime.utcnow()
        else:
            # Создаем новый прогресс
            progress = UserTheoryProgress(
                id=str(uuid4()),
                userId=user_id,
                cardId=card_id,
                createdAt=datetime.utcnow(),
                updatedAt=datetime.utcnow(),
                **progress_data
            )
            self.session.add(progress)
        
        return progress
    
    async def get_due_theory_cards(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[TheoryCard]:
        """Получение карточек для повторения"""
        now = datetime.utcnow()
        
        # Карточки со сроком повторения
        due_cards = self.session.query(TheoryCard).join(UserTheoryProgress).filter(
            and_(
                UserTheoryProgress.userId == user_id,
                UserTheoryProgress.dueDate <= now,
                UserTheoryProgress.cardState != CardState.NEW
            )
        ).limit(limit).all()
        
        # Если не хватает карточек, добавляем новые
        if len(due_cards) < limit:
            remaining_limit = limit - len(due_cards)
            
            # Карточки без прогресса
            new_cards_subquery = self.session.query(UserTheoryProgress.cardId).filter(
                UserTheoryProgress.userId == user_id
            ).subquery()
            
            new_cards = self.session.query(TheoryCard).filter(
                ~TheoryCard.id.in_(new_cards_subquery)
            ).limit(remaining_limit).all()
            
            due_cards.extend(new_cards)
        
        return due_cards
    
    async def get_theory_stats(self, user_id: int) -> Dict[str, Any]:
        """Получение статистики изучения теории пользователя"""
        # Общее количество карточек
        total_cards = self.session.query(func.count(TheoryCard.id)).scalar() or 0
        
        # Изученные карточки
        studied_cards = self.session.query(func.count(UserTheoryProgress.id)).filter(
            and_(
                UserTheoryProgress.userId == user_id,
                UserTheoryProgress.solvedCount > 0
            )
        ).scalar() or 0
        
        # Карточки для повторения
        now = datetime.utcnow()
        due_cards = self.session.query(func.count(UserTheoryProgress.id)).filter(
            and_(
                UserTheoryProgress.userId == user_id,
                UserTheoryProgress.dueDate <= now
            )
        ).scalar() or 0
        
        # Средний ease factor
        avg_ease = self.session.query(func.avg(UserTheoryProgress.easeFactor)).filter(
            UserTheoryProgress.userId == user_id
        ).scalar() or 2.5
        
        return {
            "totalCards": total_cards,
            "studiedCards": studied_cards,
            "dueCards": due_cards,
            "averageEaseFactor": float(avg_ease),
            "studyProgress": (studied_cards / total_cards * 100) if total_cards > 0 else 0
        }
    
    async def reset_card_progress(self, user_id: int, card_id: str) -> bool:
        """Сброс прогресса по карточке"""
        progress = await self.get_user_theory_progress(user_id, card_id)
        if progress:
            self.session.delete(progress)
            return True
        return False 