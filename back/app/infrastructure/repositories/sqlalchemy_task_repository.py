"""Реализация репозитория заданий для SQLAlchemy"""

from typing import List, Optional, Tuple

from sqlalchemy import asc, func, or_
from sqlalchemy.orm import Session, joinedload

from app.domain.entities.task_types import Task, TaskCategory, TaskCompany
from app.domain.repositories.task_repository import TaskRepository
from app.infrastructure.models.content_models import (
    ContentBlock,
    ContentFile,
    UserContentProgress,
)
from app.infrastructure.models.theory_models import TheoryCard, UserTheoryProgress


class SQLAlchemyTaskRepository(TaskRepository):
    """Реализация репозитория заданий для SQLAlchemy"""

    def __init__(self, session: Session):
        self.session = session

    def _unescape_text_content(self, text: Optional[str]) -> Optional[str]:
        """Заменяет экранированные символы на настоящие переносы строк"""
        if not text:
            return text
        return text.replace("\\n", "\n").replace("\\t", "\t")

    def _sort_tasks(
        self, tasks: List[Task], sort_by: str, sort_order: str
    ) -> List[Task]:
        """Сортировка списка заданий"""

        def get_sort_key(task: Task):
            sort_key = task.order_in_file or 0
            if sort_by in ("orderInFile", "orderIndex"):
                sort_key = task.order_in_file or 0
            elif sort_by == "createdAt":
                sort_key = task.created_at
            elif sort_by == "updatedAt":
                sort_key = task.updated_at
            elif sort_by == "title":
                sort_key = task.title.lower()
            elif sort_by == "category":
                sort_key = task.main_category.lower()
            elif sort_by == "subCategory":
                sort_key = (task.sub_category or "").lower()
            return sort_key

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
        user_id: Optional[int] = None,
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
                user_id=user_id,
            )
            all_tasks.extend(content_tasks)

        # Получаем theory quizzes (только если нет фильтра по компаниям)
        if (not item_type or item_type in ["theory_quiz", "all"]) and not companies:
            theory_tasks = await self.get_theory_quizzes(
                main_categories=main_categories,
                sub_categories=sub_categories,
                search_query=search_query,
                only_unsolved=only_unsolved,
                user_id=user_id,
            )
            all_tasks.extend(theory_tasks)

        # Сортировка
        all_tasks = self._sort_tasks(all_tasks, sort_by, sort_order)

        # Пагинация
        total = len(all_tasks)
        offset = (page - 1) * limit
        paginated_tasks = all_tasks[offset : offset + limit]

        return paginated_tasks, total

    async def get_content_blocks(
        self,
        main_categories: Optional[List[str]] = None,
        sub_categories: Optional[List[str]] = None,
        search_query: Optional[str] = None,
        only_unsolved: Optional[bool] = None,
        companies: Optional[List[str]] = None,
        user_id: Optional[int] = None,
    ) -> List[Task]:
        """Получение заданий типа content_block"""
        query = (
            self.session.query(ContentBlock)
            .join(ContentFile)
            .options(joinedload(ContentBlock.file))
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

        if search_query and search_query.strip():
            search_term = f"%{search_query.strip()}%"
            query = query.filter(
                or_(
                    ContentBlock.blockTitle.ilike(search_term),
                    ContentBlock.textContent.ilike(search_term),
                    ContentBlock.codeFoldTitle.ilike(search_term),
                )
            )

        if companies:
            # Фильтр по массиву компаний
            query = query.filter(ContentBlock.companies.op("&&")(companies))

        blocks = query.order_by(asc(ContentBlock.orderInFile)).all()

        # Получение прогресса пользователя
        progress_map = {}
        if user_id and blocks:
            block_ids = [block.id for block in blocks]
            progresses = (
                self.session.query(UserContentProgress)
                .filter(
                    UserContentProgress.userId == user_id,
                    UserContentProgress.blockId.in_(block_ids),
                )
                .all()
            )
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
        user_id: Optional[int] = None,
    ) -> List[Task]:
        """Получение заданий типа theory_quiz"""
        query = self.session.query(TheoryCard).filter(
            TheoryCard.category.ilike("%QUIZ%")
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
                    TheoryCard.subCategory.ilike(search_term),
                )
            )

        cards = query.order_by(asc(TheoryCard.orderIndex)).all()

        # Получение прогресса пользователя
        progress_map = {}
        if user_id and cards:
            card_ids = [card.id for card in cards]
            progresses = (
                self.session.query(UserTheoryProgress)
                .filter(
                    UserTheoryProgress.userId == user_id,
                    UserTheoryProgress.cardId.in_(card_ids),
                )
                .all()
            )
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
        # Получаем статистику по content blocks
        content_stats_query = (
            self.session.query(
                ContentFile.mainCategory,
                ContentFile.subCategory,
                func.count(ContentBlock.id).label("count"),
            )
            .join(ContentBlock)
            .group_by(ContentFile.mainCategory, ContentFile.subCategory)
            .all()
        )

        # Получаем статистику по theory cards (только QUIZ)
        theory_stats = (
            self.session.query(
                TheoryCard.category,
                TheoryCard.subCategory,
                func.count(TheoryCard.id).label("count"),
            )
            .filter(TheoryCard.category.ilike("%QUIZ%"))
            .group_by(TheoryCard.category, TheoryCard.subCategory)
            .all()
        )

        # Объединяем статистику
        categories_map = {}

        for category, sub_category, count in content_stats_query:
            if category not in categories_map:
                categories_map[category] = {
                    "name": category,
                    "subCategories": set(),
                    "contentBlockCount": 0,
                    "theoryQuizCount": 0,
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
                    "theoryQuizCount": 0,
                }

            if sub_category:
                categories_map[category]["subCategories"].add(sub_category)
            categories_map[category]["theoryQuizCount"] += count

        # Преобразуем в TaskCategory
        categories = []
        for cat_name, cat_data in categories_map.items():
            category = TaskCategory(
                main_category=cat_name,
                sub_category=None,  # Можно добавить логику для подкатегорий если нужно
                task_count=cat_data["contentBlockCount"] + cat_data["theoryQuizCount"],
            )
            categories.append(category)

        return sorted(categories, key=lambda x: x.main_category)

    async def get_task_companies(
        self,
        main_categories: Optional[List[str]] = None,
        sub_categories: Optional[List[str]] = None,
    ) -> List[TaskCompany]:
        """Получение списка компаний из заданий с количеством"""
        # Получаем все content blocks с компаниями
        query = self.session.query(ContentBlock.companies).join(ContentFile)

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

        all_companies_lists = [
            item[0] for item in query.filter(ContentBlock.companies.isnot(None)).all()
        ]

        # Разворачиваем списки и считаем
        company_counts = {}
        for company_list in all_companies_lists:
            for company in company_list:
                company_counts[company] = company_counts.get(company, 0) + 1

        # Преобразуем в список TaskCompany
        return [
            TaskCompany(name=name, taskCount=count)
            for name, count in company_counts.items()
        ]
