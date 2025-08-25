"""Сервис для агрегации задач из разных источников"""

import logging
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.features.task.dto.responses import (
    TaskCategoryResponse as TaskCategory,
    TaskCompanyResponse as TaskCompany,
)
from app.features.task.repositories.content_block_repository import (
    ContentBlockRepository,
)
from app.features.task.repositories.theory_quiz_repository import TheoryQuizRepository
from app.shared.schemas.task import Task

logger = logging.getLogger(__name__)


class TaskAggregatorService:
    """Сервис для агрегации задач из разных репозиториев"""

    def __init__(self, session: Session):
        self.content_block_repo = ContentBlockRepository(session)
        self.theory_quiz_repo = TheoryQuizRepository(session)

    def get_tasks(
        self,
        user_id: Optional[int] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        company: Optional[str] = None,
        task_type: Optional[str] = None,
        sort_by: str = "orderInFile",
        sort_order: str = "asc",
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Tuple[List[Task], int]:
        """Получить задачи из всех источников с унифицированной фильтрацией и сортировкой"""

        all_tasks = []
        total_count = 0

        # Получение блоков контента
        if task_type is None or task_type == "content_block":
            content_tasks, content_count = self.content_block_repo.get_content_blocks(
                user_id=user_id,
                category=category,
                search=search,
                company=company,
                limit=None,  # Получаем все для сортировки
                offset=None,
            )
            all_tasks.extend(content_tasks)
            total_count += content_count

        # Получение теоретических тестов
        if task_type is None or task_type == "theory_quiz":
            # Теоретические тесты не имеют компании, поэтому фильтруем только если компания не указана
            if company is None:
                theory_tasks, theory_count = self.theory_quiz_repo.get_theory_quizzes(
                    user_id=user_id,
                    category=category,
                    search=search,
                    limit=None,  # Получаем все для сортировки
                    offset=None,
                )
                all_tasks.extend(theory_tasks)
                total_count += theory_count

        # Сортировка объединенного списка
        sorted_tasks = self._sort_tasks(all_tasks, sort_by, sort_order)

        # Применение пагинации после сортировки
        start_idx = offset or 0
        end_idx = start_idx + limit if limit else len(sorted_tasks)
        paginated_tasks = sorted_tasks[start_idx:end_idx]

        logger.info(
            f"Retrieved {len(paginated_tasks)} tasks out of {total_count} total",
            user_id=user_id,
            category=category,
            task_type=task_type,
        )

        return paginated_tasks, total_count

    def _sort_tasks(
        self, tasks: List[Task], sort_by: str, sort_order: str
    ) -> List[Task]:
        """Сортировка списка заданий"""

        def get_sort_key(task: Task):
            sort_key = task.order_in_file or 0
            if sort_by in ("orderInFile", "orderIndex"):
                sort_key = task.order_in_file or 0
            elif sort_by == "title":
                sort_key = task.title or ""
            elif sort_by == "category":
                sort_key = task.category or ""
            elif sort_by == "company":
                sort_key = task.company or ""
            elif sort_by == "difficulty":
                sort_key = task.difficulty or ""
            elif sort_by == "type":
                sort_key = task.type or ""
            elif sort_by == "progress":
                sort_key = task.progress_percentage or 0
            elif sort_by == "completed":
                sort_key = 1 if task.is_completed else 0

            return sort_key

        reverse = sort_order == "desc"
        return sorted(tasks, key=get_sort_key, reverse=reverse)

    def get_task_categories(self) -> List[TaskCategory]:
        """Получить все категории задач из всех источников"""

        # Получаем категории из блоков контента
        content_categories = self.content_block_repo.get_content_block_categories()

        # Получаем категории из теоретических тестов
        theory_categories = self.theory_quiz_repo.get_theory_quiz_categories()

        # Объединяем и убираем дубликаты
        all_categories = list(set(content_categories + theory_categories))
        all_categories.sort()

        # Подсчитываем количество задач в каждой категории
        categories_with_counts = []
        for category in all_categories:
            # Подсчет для блоков контента
            content_tasks, content_count = self.content_block_repo.get_content_blocks(
                category=category, limit=0
            )

            # Подсчет для теоретических тестов
            theory_tasks, theory_count = self.theory_quiz_repo.get_theory_quizzes(
                category=category, limit=0
            )

            total_count = content_count + theory_count

            categories_with_counts.append(
                TaskCategory(name=category, count=total_count)
            )

        return categories_with_counts

    def get_task_companies(self) -> List[TaskCompany]:
        """Получить все компании из задач (только из блоков контента)"""

        # Только блоки контента имеют компании
        companies = self.content_block_repo.get_content_block_companies()
        companies.sort()

        # Подсчитываем количество задач для каждой компании
        companies_with_counts = []
        for company in companies:
            content_tasks, content_count = self.content_block_repo.get_content_blocks(
                company=company, limit=0
            )

            companies_with_counts.append(TaskCompany(name=company, count=content_count))

        return companies_with_counts

    def search_tasks(
        self,
        search_query: str,
        user_id: Optional[int] = None,
        limit: int = 50,
    ) -> List[Task]:
        """Поиск задач по всем источникам"""

        if not search_query or len(search_query.strip()) < 2:
            return []

        all_tasks, _ = self.get_tasks(
            user_id=user_id,
            search=search_query.strip(),
            limit=limit,
            sort_by="title",
            sort_order="asc",
        )

        return all_tasks
