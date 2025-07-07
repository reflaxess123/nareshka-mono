"""Реализация репозитория заданий для SQLAlchemy"""

from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import and_, func, or_, asc, desc, text
from sqlalchemy.orm import Session

from ...domain.entities.task import Task, TaskCategory, TaskCompany, TaskType
from ..models.content_models import ContentBlock, UserContentProgress
from ..models.theory_models import TheoryCard, UserTheoryProgress
from ...domain.repositories.task_repository import TaskRepository


class SQLAlchemyTaskRepository(TaskRepository):
    """Реализация репозитория заданий для SQLAlchemy"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def _unescape_text_content(self, text: Optional[str]) -> Optional[str]:
        """Заменяет экранированные символы на настоящие переносы строк"""
        if not text:
            return text
        return text.replace("\\n", "\n").replace("\\t", "\t")
    
    def _sort_tasks(self, tasks: List[Task], sort_by: str, sort_order: str) -> List[Task]:
        """Сортировка списка заданий"""
        def get_sort_key(task: Task):
            if sort_by == "orderInFile":
                return task.orderInFile or 0
            elif sort_by == "orderIndex":
                return task.orderIndex or 0
            elif sort_by == "createdAt":
                return task.createdAt
            elif sort_by == "updatedAt":
                return task.updatedAt
            elif sort_by == "title":
                return task.title.lower()
            elif sort_by == "category":
                return task.category.lower()
            elif sort_by == "subCategory":
                return (task.subCategory or "").lower()
            else:
                return task.orderInFile or 0
        
        reverse = sort_order == "desc"
        return sorted(tasks, key=get_sort_key, reverse=reverse)
    
    async def get_tasks(
        self,
        page: int = 1,
        limit: int = 10,
        main_categories: Optional[List[str]] = None,
        sub_categories: Optional[List[str]] = None,
        search_query: Optional[str] = None,
        sort_by: str = "orderInFile",
        sort_order: str = "asc",
        item_type: Optional[str] = None,
        only_unsolved: Optional[bool] = None,
        companies: Optional[List[str]] = None,
        user_id: Optional[int] = None
    ) -> Tuple[List[Task], int]:
        """Получение объединенного списка заданий с пагинацией и фильтрацией"""
        all_tasks = []
        
        # Получаем content blocks
        if not item_type or item_type in ["content_block", "all"]:
            content_tasks = await self.get_content_blocks(
                main_categories=main_categories,
                sub_categories=sub_categories,
                search_query=search_query,
                only_unsolved=only_unsolved,
                companies=companies,
                user_id=user_id
            )
            all_tasks.extend(content_tasks)
        
        # Получаем theory quizzes (только если нет фильтра по компаниям)
        if not item_type or item_type in ["theory_quiz", "all"]:
            if not companies:
                theory_tasks = await self.get_theory_quizzes(
                    main_categories=main_categories,
                    sub_categories=sub_categories,
                    search_query=search_query,
                    only_unsolved=only_unsolved,
                    user_id=user_id
                )
                all_tasks.extend(theory_tasks)
        
        # Сортировка
        all_tasks = self._sort_tasks(all_tasks, sort_by, sort_order)
        
        # Пагинация
        total = len(all_tasks)
        offset = (page - 1) * limit
        paginated_tasks = all_tasks[offset:offset + limit]
        
        return paginated_tasks, total
    
    async def get_content_blocks(
        self,
        main_categories: Optional[List[str]] = None,
        sub_categories: Optional[List[str]] = None,
        search_query: Optional[str] = None,
        only_unsolved: Optional[bool] = None,
        companies: Optional[List[str]] = None,
        user_id: Optional[int] = None
    ) -> List[Task]:
        """Получение заданий типа content_block"""
        from ..models.content_models import ContentFile
        
        query = self.session.query(ContentBlock).join(ContentFile)
        
        # Фильтры
        if main_categories:
            query = query.filter(
                func.lower(ContentFile.mainCategory).in_(
                    [cat.lower() for cat in main_categories]
                )
            )
        
        if sub_categories:
            query = query.filter(
                func.lower(ContentFile.subCategory).in_(
                    [cat.lower() for cat in sub_categories]
                )
            )
        
        if search_query and search_query.strip():
            search_term = f"%{search_query.strip()}%"
            query = query.filter(
                or_(
                    ContentBlock.blockTitle.ilike(search_term),
                    ContentBlock.textContent.ilike(search_term),
                    ContentBlock.codeFoldTitle.ilike(search_term)
                )
            )
        
        if companies:
            # Фильтр по массиву компаний
            query = query.filter(
                ContentBlock.companies.op('&&')(companies)
            )
        
        blocks = query.order_by(asc(ContentBlock.orderInFile)).all()
        
        # Получение прогресса пользователя
        progress_map = {}
        if user_id and blocks:
            block_ids = [block.id for block in blocks]
            progresses = self.session.query(UserContentProgress).filter(
                UserContentProgress.userId == user_id,
                UserContentProgress.blockId.in_(block_ids)
            ).all()
            progress_map = {p.blockId: p for p in progresses}
        
        # Преобразование в Task
        tasks = []
        for block in blocks:
            progress = progress_map.get(block.id)
            
            # Фильтр нерешенных
            if only_unsolved and progress and progress.solvedCount > 0:
                continue
            
            # Исправление текста
            if block.textContent:
                block.textContent = self._unescape_text_content(block.textContent)
            
            task = Task.from_content_block(block, progress)
            tasks.append(task)
        
        return tasks
    
    async def get_theory_quizzes(
        self,
        main_categories: Optional[List[str]] = None,
        sub_categories: Optional[List[str]] = None,
        search_query: Optional[str] = None,
        only_unsolved: Optional[bool] = None,
        user_id: Optional[int] = None
    ) -> List[Task]:
        """Получение заданий типа theory_quiz"""
        query = self.session.query(TheoryCard).filter(
            TheoryCard.category.ilike('%QUIZ%')
        )
        
        # Фильтры
        if main_categories:
            query = query.filter(
                func.lower(TheoryCard.category).in_(
                    [cat.lower() for cat in main_categories]
                )
            )
        
        if sub_categories:
            query = query.filter(
                func.lower(TheoryCard.subCategory).in_(
                    [cat.lower() for cat in sub_categories]
                )
            )
        
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
        
        cards = query.order_by(asc(TheoryCard.orderIndex)).all()
        
        # Получение прогресса пользователя
        progress_map = {}
        if user_id and cards:
            card_ids = [card.id for card in cards]
            progresses = self.session.query(UserTheoryProgress).filter(
                UserTheoryProgress.userId == user_id,
                UserTheoryProgress.cardId.in_(card_ids)
            ).all()
            progress_map = {p.cardId: p for p in progresses}
        
        # Преобразование в Task
        tasks = []
        for card in cards:
            progress = progress_map.get(card.id)
            
            # Фильтр нерешенных
            if only_unsolved and progress and progress.solvedCount > 0:
                continue
            
            task = Task.from_theory_card(card, progress)
            tasks.append(task)
        
        return tasks
    
    async def get_task_categories(self) -> List[TaskCategory]:
        """Получение списка категорий заданий с подкатегориями и статистикой"""
        from ..models.content_models import ContentFile
        
        # Получаем статистику по content blocks
        content_stats = self.session.query(
            ContentFile.mainCategory,
            ContentFile.subCategory,
            func.count(ContentBlock.id).label("count")
        ).join(ContentBlock).group_by(
            ContentFile.mainCategory, ContentFile.subCategory
        ).all()
        
        # Получаем статистику по theory cards (только QUIZ)
        theory_stats = self.session.query(
            TheoryCard.category,
            TheoryCard.subCategory,
            func.count(TheoryCard.id).label("count")
        ).filter(
            TheoryCard.category.ilike('%QUIZ%')
        ).group_by(
            TheoryCard.category, TheoryCard.subCategory
        ).all()
        
        # Объединяем статистику
        categories_map = {}
        
        for category, sub_category, count in content_stats:
            if category not in categories_map:
                categories_map[category] = {
                    "name": category,
                    "subCategories": set(),
                    "contentBlockCount": 0,
                    "theoryQuizCount": 0
                }
            
            if sub_category:
                categories_map[category]["subCategories"].add(sub_category)
            categories_map[category]["contentBlockCount"] += count
        
        for category, sub_category, count in theory_stats:
            if category not in categories_map:
                categories_map[category] = {
                    "name": category,
                    "subCategories": set(),
                    "contentBlockCount": 0,
                    "theoryQuizCount": 0
                }
            
            if sub_category:
                categories_map[category]["subCategories"].add(sub_category)
            categories_map[category]["theoryQuizCount"] += count
        
        # Преобразуем в TaskCategory
        categories = []
        for cat_name, cat_data in categories_map.items():
            category = TaskCategory(
                name=cat_name,
                subCategories=sorted(list(cat_data["subCategories"])),
                totalCount=cat_data["contentBlockCount"] + cat_data["theoryQuizCount"],
                contentBlockCount=cat_data["contentBlockCount"],
                theoryQuizCount=cat_data["theoryQuizCount"]
            )
            categories.append(category)
        
        return sorted(categories, key=lambda x: x.name)
    
    async def get_task_companies(
        self,
        main_categories: Optional[List[str]] = None,
        sub_categories: Optional[List[str]] = None
    ) -> List[TaskCompany]:
        """Получение списка компаний из заданий с количеством"""
        from ..models.content_models import ContentFile
        
        # Получаем все content blocks с компаниями
        query = self.session.query(ContentBlock).join(ContentFile).filter(
            ContentBlock.companies.isnot(None)
        )
        
        # Фильтры
        if main_categories:
            query = query.filter(
                func.lower(ContentFile.mainCategory).in_(
                    [cat.lower() for cat in main_categories]
                )
            )
        
        if sub_categories:
            query = query.filter(
                func.lower(ContentFile.subCategory).in_(
                    [cat.lower() for cat in sub_categories]
                )
            )
        
        blocks = query.all()
        
        # Подсчет компаний
        company_counts = {}
        for block in blocks:
            if block.companies:
                for company in block.companies:
                    company_counts[company] = company_counts.get(company, 0) + 1
        
        # Преобразование в TaskCompany
        companies = [
            TaskCompany(name=name, count=count)
            for name, count in company_counts.items()
        ]
        
        return sorted(companies, key=lambda x: (-x.count, x.name)) 