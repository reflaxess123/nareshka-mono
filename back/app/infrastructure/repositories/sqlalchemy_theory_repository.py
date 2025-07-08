"""Реализация репозитория теоретических карточек для SQLAlchemy"""

from typing import List, Optional, Tuple, Dict, Any
from uuid import uuid4
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import and_, func, or_, asc, desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from ...domain.repositories.theory_repository import TheoryRepository
from ...domain.entities.theory_types import TheoryCard as DomainTheoryCard, UserTheoryProgress as DomainUserTheoryProgress
from ...domain.entities.enums import CardState
from ..models.theory_models import TheoryCard as SQLTheoryCard, UserTheoryProgress as SQLUserTheoryProgress


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
    ) -> Tuple[List[DomainTheoryCard], int]:
        """Получение теоретических карточек с пагинацией и фильтрацией"""
        offset = (page - 1) * limit
        
        query = self.session.query(SQLTheoryCard).filter(
            ~SQLTheoryCard.category.ilike('%QUIZ%'),
            ~SQLTheoryCard.category.ilike('%ПРАКТИКА%')
        )
        
        # Фильтры
        if category:
            query = query.filter(func.lower(SQLTheoryCard.category) == func.lower(category))
        
        if sub_category:
            query = query.filter(func.lower(SQLTheoryCard.subCategory) == func.lower(sub_category))
        
        if deck:
            query = query.filter(SQLTheoryCard.deck.ilike(f"%{deck}%"))
        
        # Поиск
        if search_query and search_query.strip():
            search_term = f"%{search_query.strip()}%"
            query = query.filter(
                or_(
                    SQLTheoryCard.questionBlock.ilike(search_term),
                    SQLTheoryCard.answerBlock.ilike(search_term),
                    SQLTheoryCard.category.ilike(search_term),
                    SQLTheoryCard.subCategory.ilike(search_term)
                )
            )
        
        # Фильтр неизученных карточек
        if only_unstudied and user_id:
            studied_card_ids = self.session.query(SQLUserTheoryProgress.cardId).filter(
                SQLUserTheoryProgress.userId == user_id,
                SQLUserTheoryProgress.solvedCount > 0
            ).subquery()
            
            query = query.filter(~SQLTheoryCard.id.in_(studied_card_ids))
        
        # Сортировка
        if sort_by == "createdAt":
            order_field = SQLTheoryCard.createdAt
        elif sort_by == "updatedAt":
            order_field = SQLTheoryCard.updatedAt
        elif sort_by == "orderIndex":
            order_field = SQLTheoryCard.orderIndex
        else:
            order_field = SQLTheoryCard.orderIndex
        
        if sort_order == "desc":
            query = query.order_by(desc(order_field))
        else:
            query = query.order_by(asc(order_field))
        
        total = query.count()
        infra_cards = query.offset(offset).limit(limit).all()
        
        # Конвертируем Infrastructure модели в Domain entities
        domain_cards = TheoryMapper.theory_card_list_to_domain(infra_cards)
        
        return domain_cards, total
    
    async def get_theory_card_by_id(self, card_id: str) -> Optional[DomainTheoryCard]:
        """Получение теоретической карточки по ID"""
        infra_card = self.session.query(SQLTheoryCard).filter(SQLTheoryCard.id == card_id).first()
        return TheoryMapper.theory_card_to_domain(infra_card) if infra_card else None
    
    async def get_theory_categories(self) -> List[Dict[str, Any]]:
        """Получение списка категорий с подкатегориями и количеством карточек"""
        categories_data = self.session.query(
            SQLTheoryCard.category,
            SQLTheoryCard.subCategory,
            func.count(SQLTheoryCard.id).label("count")
        ).filter(
            ~SQLTheoryCard.category.ilike('%QUIZ%'),
            ~SQLTheoryCard.category.ilike('%ПРАКТИКА%')
        ).group_by(SQLTheoryCard.category, SQLTheoryCard.subCategory).all()
        
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
            row[0] for row in self.session.query(SQLTheoryCard.subCategory)
            .filter(
                func.lower(SQLTheoryCard.category) == func.lower(category),
                SQLTheoryCard.subCategory.isnot(None)
            )
            .distinct()
            .order_by(SQLTheoryCard.subCategory)
            .all()
        ]
    
    async def get_user_theory_progress(
        self, 
        user_id: int, 
        card_id: str
    ) -> Optional[DomainUserTheoryProgress]:
        """Получение прогресса пользователя по карточке"""
        infra_progress = self.session.query(SQLUserTheoryProgress).filter(
            and_(
                SQLUserTheoryProgress.userId == user_id,
                SQLUserTheoryProgress.cardId == card_id
            )
        ).first()
        return TheoryMapper.user_theory_progress_to_domain(infra_progress) if infra_progress else None
    
    async def create_or_update_user_progress(
        self,
        user_id: int,
        card_id: str,
        **progress_data
    ) -> DomainUserTheoryProgress:
        """Создание или обновление прогресса пользователя"""
        infra_progress = self.session.query(SQLUserTheoryProgress).filter(
            and_(
                SQLUserTheoryProgress.userId == user_id,
                SQLUserTheoryProgress.cardId == card_id
            )
        ).first()
        
        if infra_progress:
            # Обновляем существующий прогресс
            for key, value in progress_data.items():
                if hasattr(infra_progress, key):
                    setattr(infra_progress, key, value)
            infra_progress.updatedAt = datetime.utcnow()
        else:
            # Создаем новый прогресс
            infra_progress = SQLUserTheoryProgress(
                id=str(uuid4()),
                userId=user_id,
                cardId=card_id,
                createdAt=datetime.utcnow(),
                updatedAt=datetime.utcnow(),
                **progress_data
            )
            self.session.add(infra_progress)
        
        return TheoryMapper.user_theory_progress_to_domain(infra_progress)
    
    async def get_due_theory_cards(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[DomainTheoryCard]:
        """Получение карточек для повторения"""
        now = datetime.utcnow()
        
        # Карточки со сроком повторения
        due_infra_cards = self.session.query(SQLTheoryCard).join(SQLUserTheoryProgress).filter(
            and_(
                SQLUserTheoryProgress.userId == user_id,
                SQLUserTheoryProgress.dueDate <= now,
                SQLUserTheoryProgress.cardState != CardState.NEW
            )
        ).limit(limit).all()
        
        # Если не хватает карточек, добавляем новые
        if len(due_infra_cards) < limit:
            remaining_limit = limit - len(due_infra_cards)
            
            # Карточки без прогресса
            new_cards_subquery = self.session.query(SQLUserTheoryProgress.cardId).filter(
                SQLUserTheoryProgress.userId == user_id
            ).subquery()
            
            new_infra_cards = self.session.query(SQLTheoryCard).filter(
                ~SQLTheoryCard.id.in_(new_cards_subquery)
            ).limit(remaining_limit).all()
            
            due_infra_cards.extend(new_infra_cards)
        
        return TheoryMapper.theory_card_list_to_domain(due_infra_cards)
    
    async def get_theory_stats(self, user_id: int) -> Dict[str, Any]:
        """Получение статистики изучения теории пользователя"""
        # Общее количество карточек
        total_cards = self.session.query(func.count(SQLTheoryCard.id)).filter(
            ~SQLTheoryCard.category.ilike('%QUIZ%'),
            ~SQLTheoryCard.category.ilike('%ПРАКТИКА%')
        ).scalar() or 0
        
        # Изученные карточки
        studied_cards = self.session.query(func.count(SQLUserTheoryProgress.id)).filter(
            SQLUserTheoryProgress.userId == user_id,
            SQLUserTheoryProgress.solvedCount > 0
        ).scalar() or 0
        
        # Статистика по категориям
        category_stats = self.session.query(
            SQLTheoryCard.category,
            func.count(SQLTheoryCard.id).label('total'),
            func.count(SQLUserTheoryProgress.id).label('studied')
        ).outerjoin(
            SQLUserTheoryProgress, 
            and_(
                SQLUserTheoryProgress.cardId == SQLTheoryCard.id,
                SQLUserTheoryProgress.userId == user_id,
                SQLUserTheoryProgress.solvedCount > 0
            )
        ).filter(
            ~SQLTheoryCard.category.ilike('%QUIZ%'),
            ~SQLTheoryCard.category.ilike('%ПРАКТИКА%')
        ).group_by(SQLTheoryCard.category).all()
        
        categories = []
        for category, total, studied in category_stats:
            categories.append({
                'category': category,
                'totalCards': total,
                'studiedCards': studied or 0,
                'progress': (studied or 0) / total * 100 if total > 0 else 0
            })
        
        return {
            'totalCards': total_cards,
            'studiedCards': studied_cards,
            'progress': studied_cards / total_cards * 100 if total_cards > 0 else 0,
            'categories': categories
        }
    
    async def reset_card_progress(self, user_id: int, card_id: str) -> bool:
        """Сброс прогресса по карточке"""
        progress = self.session.query(SQLUserTheoryProgress).filter(
            and_(
                SQLUserTheoryProgress.userId == user_id,
                SQLUserTheoryProgress.cardId == card_id
            )
        ).first()
        
        if progress:
            self.session.delete(progress)
            return True
        
        return False 