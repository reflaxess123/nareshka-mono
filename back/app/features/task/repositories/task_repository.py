"""Репозиторий для работы с заданиями - DEPRECATED - используйте TaskAggregatorService"""

import html
import logging
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import uuid4

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.features.task.dto.responses import (
    TaskCategoryResponse as TaskCategory,
    TaskCompanyResponse as TaskCompany,
)
from app.features.task.repositories.task_attempt_repository import TaskAttemptRepository
from app.features.task.services.task_aggregator_service import TaskAggregatorService
from app.shared.entities.content import ContentBlock, ContentFile
from app.shared.entities.progress_types import TaskAttempt, TaskSolution
from app.shared.entities.task_types import Task
from app.shared.models.content_models import UserContentProgress
from app.shared.models.theory_models import TheoryCard, UserTheoryProgress

logger = logging.getLogger(__name__)


class TaskRepository:
    """
    DEPRECATED: Этот класс больше не используется.
    Используйте TaskAggregatorService для получения задач.
    Используйте TaskAttemptRepository для работы с попытками и решениями.
    """

    def __init__(self, session: Session):
        self.session = session
        # Создаем экземпляры новых сервисов для обратной совместимости
        self._aggregator = TaskAggregatorService(session)
        self._attempt_repo = TaskAttemptRepository(session)

    # Методы делегируются к новым сервисам для обратной совместимости

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
        """DEPRECATED: Используйте TaskAggregatorService.get_tasks()"""
        return self._aggregator.get_tasks(
            user_id=user_id,
            category=category,
            search=search,
            company=company,
            task_type=task_type,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
        )

    def get_task_categories(self) -> List[TaskCategory]:
        """DEPRECATED: Используйте TaskAggregatorService.get_task_categories()"""
        return self._aggregator.get_task_categories()

    def get_task_companies(self) -> List[TaskCompany]:
        """DEPRECATED: Используйте TaskAggregatorService.get_task_companies()"""
        return self._aggregator.get_task_companies()

    async def create_task_attempt(self, user_id: int, **attempt_data) -> TaskAttempt:
        """DEPRECATED: Используйте TaskAttemptRepository.create_task_attempt()"""
        # Извлекаем нужные параметры из attempt_data
        task_id = attempt_data.get("task_id") or attempt_data.get("blockId")
        task_type = attempt_data.get("task_type", "content_block")
        code = attempt_data.get("code", "")
        language = attempt_data.get("language", "")

        return self._attempt_repo.create_task_attempt(
            user_id=user_id,
            task_id=task_id,
            task_type=task_type,
            code=code,
            language=language,
        )

    async def create_task_solution(self, user_id: int, **solution_data) -> TaskSolution:
        """DEPRECATED: Используйте TaskAttemptRepository.create_task_solution()"""
        # Извлекаем нужные параметры из solution_data
        task_id = solution_data.get("task_id") or solution_data.get("blockId")
        task_type = solution_data.get("task_type", "content_block")
        code = solution_data.get("code", "")
        language = solution_data.get("language", "")
        is_correct = solution_data.get("is_correct", False)
        execution_time = solution_data.get("execution_time")
        memory_usage = solution_data.get("memory_usage")
        test_results = solution_data.get("test_results")

        return self._attempt_repo.create_task_solution(
            user_id=user_id,
            task_id=task_id,
            task_type=task_type,
            code=code,
            language=language,
            is_correct=is_correct,
            execution_time=execution_time,
            memory_usage=memory_usage,
            test_results=test_results,
        )

    async def get_user_task_attempts(
        self, user_id: int, block_id: Optional[str] = None
    ) -> List[TaskAttempt]:
        """DEPRECATED: Используйте TaskAttemptRepository.get_user_task_attempts()"""
        task_id = int(block_id) if block_id and block_id.isdigit() else None
        return self._attempt_repo.get_user_task_attempts(
            user_id=user_id, task_id=task_id
        )

    async def get_user_task_solutions(
        self, user_id: int, block_id: Optional[str] = None
    ) -> List[TaskSolution]:
        """DEPRECATED: Используйте TaskAttemptRepository.get_user_task_solutions()"""
        task_id = int(block_id) if block_id and block_id.isdigit() else None
        return self._attempt_repo.get_user_task_solutions(
            user_id=user_id, task_id=task_id
        )

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
        """Получение контентных блоков как заданий"""

        query = (
            self.session.query(ContentBlock)
            .join(ContentFile)
            # .filter(ContentBlock.blockType.in_(["QUIZ", "ЗАДАЧА", "CODING"]))  # TEMPORARY FIX: blockType field doesn't exist
            .options(joinedload(ContentBlock.file))
        )

        # Фильтры
        if main_categories:
            query = query.filter(ContentFile.mainCategory.in_(main_categories))

        if sub_categories:
            query = query.filter(ContentFile.subCategory.in_(sub_categories))

        if companies:
            conditions = []
            for company in companies:
                conditions.append(ContentBlock.companies.any(company))
            if conditions:
                query = query.filter(or_(*conditions))

        if search_query:
            search_term = f"%{search_query}%"
            query = query.filter(
                or_(
                    ContentBlock.textContent.ilike(search_term),
                    ContentBlock.codeContent.ilike(search_term),
                    ContentFile.webdavPath.ilike(search_term),
                )
            )

        # Фильтр нерешённых задач
        if only_unsolved and user_id:
            solved_block_ids = (
                self.session.query(UserContentProgress.blockId)
                .filter(
                    UserContentProgress.userId == user_id,
                    UserContentProgress.solvedCount > 0,
                )
                .subquery()
            )
            query = query.filter(~ContentBlock.id.in_(solved_block_ids))

        blocks = query.order_by(ContentFile.webdavPath, ContentBlock.orderInFile).all()

        # Получаем прогресс пользователя ОДНИМ запросом
        user_progress = {}
        if user_id:
            block_ids = [block.id for block in blocks]
            if block_ids:
                progress_records = (
                    self.session.query(UserContentProgress)
                    .filter(
                        UserContentProgress.userId == user_id,
                        UserContentProgress.blockId.in_(block_ids),
                    )
                    .all()
                )
                user_progress = {p.blockId: p.solvedCount for p in progress_records}
                logger.info(
                    f"🔍 DEBUG: Found progress records: {len(progress_records)}, progress_dict: {user_progress}"
                )

                # Дополнительное логирование для отладки
                if progress_records:
                    sample_progress = progress_records[:3]
                    logger.info(
                        "🔍 DEBUG: Sample progress records",
                        extra={
                            "user_id": user_id,
                            "sample_records": [
                                {
                                    "userId": p.userId,
                                    "blockId": p.blockId[:10] + "...",
                                    "solvedCount": p.solvedCount,
                                    "createdAt": str(p.createdAt),
                                }
                                for p in sample_progress
                            ],
                        },
                    )
                else:
                    # Проверим, есть ли вообще записи для этого пользователя
                    total_user_progress = (
                        self.session.query(UserContentProgress)
                        .filter(UserContentProgress.userId == user_id)
                        .count()
                    )
                    logger.info(
                        f"🔍 DEBUG: No progress found for current blocks, but user has {total_user_progress} total progress records"
                    )
        else:
            logger.info("🔍 DEBUG: user_id is None, skipping progress loading")

        # Преобразуем в Task
        tasks = []
        for block in blocks:
            # Мапинг языков программирования
            language_mapping = {
                "js": "JAVASCRIPT",
                "javascript": "JAVASCRIPT",
                "ts": "TYPESCRIPT",
                "typescript": "TYPESCRIPT",
                "py": "PYTHON",
                "python": "PYTHON",
                "java": "JAVA",
                "cpp": "CPP",
                "c++": "CPP",
                "c": "C",
                "go": "GO",
                "rust": "RUST",
                "php": "PHP",
                "ruby": "RUBY",
                "rb": "RUBY",
            }

            # Преобразуем язык программирования
            code_language = None
            if block.codeLanguage:
                mapped_lang = language_mapping.get(block.codeLanguage.lower())
                if mapped_lang:
                    from app.shared.entities.enums import CodeLanguage

                    try:
                        code_language = CodeLanguage(mapped_lang)
                    except ValueError:
                        code_language = None

            solved_count = user_progress.get(block.id, 0)

            task = Task(
                id=block.id,
                item_type="content_block",
                title=block.blockTitle,
                description=self._unescape_text_content(block.textContent),
                main_category=block.file.mainCategory if block.file else "",
                sub_category=block.file.subCategory if block.file else None,
                file_id=block.fileId,
                file_path=block.file.webdavPath if block.file else None,
                path_titles=block.pathTitles or [],
                block_level=block.blockLevel,
                order_in_file=block.orderInFile,
                text_content=self._unescape_text_content(block.textContent),
                code_content=block.codeContent,
                code_language=code_language,
                is_code_foldable=block.isCodeFoldable,
                code_fold_title=block.codeFoldTitle,
                extracted_urls=block.extractedUrls or [],
                companies=block.companies or [],
                current_user_solved_count=solved_count,
                created_at=block.createdAt,
                updated_at=block.updatedAt,
            )
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
        """Получение теоретических квизов как заданий"""

        query = self.session.query(TheoryCard).filter(
            or_(
                TheoryCard.category.ilike("%QUIZ%"),
                TheoryCard.category.ilike("%ПРАКТИКА%"),
            )
        )

        # Фильтры
        if main_categories:
            query = query.filter(TheoryCard.category.in_(main_categories))

        if sub_categories:
            query = query.filter(TheoryCard.subCategory.in_(sub_categories))

        if search_query:
            search_term = f"%{search_query}%"
            query = query.filter(
                or_(
                    TheoryCard.questionBlock.ilike(search_term),
                    TheoryCard.answerBlock.ilike(search_term),
                    TheoryCard.category.ilike(search_term),
                )
            )

        # Фильтр нерешённых задач
        if only_unsolved and user_id:
            solved_card_ids = (
                self.session.query(UserTheoryProgress.cardId)
                .filter(
                    UserTheoryProgress.userId == user_id,
                    UserTheoryProgress.solvedCount > 0,
                )
                .subquery()
            )
            query = query.filter(~TheoryCard.id.in_(solved_card_ids))

        cards = query.order_by(TheoryCard.orderIndex).all()

        # Получаем прогресс пользователя
        user_progress = {}
        if user_id:
            progress_records = (
                self.session.query(UserTheoryProgress)
                .filter(UserTheoryProgress.userId == user_id)
                .all()
            )
            user_progress = {p.cardId: p.solvedCount for p in progress_records}

        # Преобразуем в Task
        tasks = []
        for card in cards:
            task = Task(
                id=card.id,
                item_type="theory_quiz",
                title=f"Квиз: {card.category}",
                description=card.questionBlock,
                main_category=card.category,
                sub_category=card.subCategory,
                file_id=None,
                file_path=None,
                path_titles=[],
                block_level=None,
                order_in_file=card.orderIndex,
                text_content=None,
                code_content=None,
                code_language=None,
                is_code_foldable=None,
                code_fold_title=None,
                extracted_urls=[],
                companies=[],
                question_block=card.questionBlock,
                answer_block=card.answerBlock,
                tags=card.tags or [],
                order_index=card.orderIndex,
                current_user_solved_count=user_progress.get(card.id, 0),
                created_at=card.createdAt,
                updated_at=card.updatedAt,
            )
            tasks.append(task)

        return tasks

    async def get_task_categories(self) -> List[TaskCategory]:
        """Получение списка категорий заданий с подкатегориями и статистикой"""

        # Категории из content blocks
        content_categories = (
            self.session.query(
                ContentFile.mainCategory,
                ContentFile.subCategory,
                func.count(ContentBlock.id).label("count"),
            )
            .join(ContentBlock)
            # .filter(ContentBlock.blockType.in_(["QUIZ", "ЗАДАЧА", "CODING"]))  # TEMPORARY FIX: blockType field doesn't exist
            .group_by(ContentFile.mainCategory, ContentFile.subCategory)
            .all()
        )

        # Категории из theory cards
        theory_categories = (
            self.session.query(
                TheoryCard.category,
                TheoryCard.subCategory,
                func.count(TheoryCard.id).label("count"),
            )
            .filter(
                or_(
                    TheoryCard.category.ilike("%QUIZ%"),
                    TheoryCard.category.ilike("%ПРАКТИКА%"),
                )
            )
            .group_by(TheoryCard.category, TheoryCard.subCategory)
            .all()
        )

        # Объединяем категории
        categories_dict = {}

        # Обрабатываем content categories
        for main_cat, sub_cat, count in content_categories:
            if main_cat not in categories_dict:
                categories_dict[main_cat] = TaskCategory(
                    name=main_cat,
                    subCategories=[],
                    totalCount=0,
                    contentBlockCount=0,
                    theoryQuizCount=0,
                )
            categories_dict[main_cat].contentBlockCount += count
            categories_dict[main_cat].totalCount += count
            if sub_cat and sub_cat not in categories_dict[main_cat].subCategories:
                categories_dict[main_cat].subCategories.append(sub_cat)

        # Обрабатываем theory categories
        for main_cat, sub_cat, count in theory_categories:
            if main_cat not in categories_dict:
                categories_dict[main_cat] = TaskCategory(
                    name=main_cat,
                    subCategories=[],
                    totalCount=0,
                    contentBlockCount=0,
                    theoryQuizCount=0,
                )
            categories_dict[main_cat].theoryQuizCount += count
            categories_dict[main_cat].totalCount += count
            if sub_cat and sub_cat not in categories_dict[main_cat].subCategories:
                categories_dict[main_cat].subCategories.append(sub_cat)

        return list(categories_dict.values())

    async def get_task_companies(
        self,
        main_categories: Optional[List[str]] = None,
        sub_categories: Optional[List[str]] = None,
    ) -> List[TaskCompany]:
        """Получение списка компаний из заданий с количеством"""

        query = (
            self.session.query(ContentBlock)
            .join(ContentFile)
            .filter(
                # ContentBlock.blockType.in_(["QUIZ", "ЗАДАЧА", "CODING"]),  # TEMPORARY FIX: blockType field doesn't exist
                ContentBlock.companies.isnot(None),
                func.array_length(ContentBlock.companies, 1) > 0,
            )
        )

        # Фильтры
        if main_categories:
            query = query.filter(ContentFile.mainCategory.in_(main_categories))

        if sub_categories:
            query = query.filter(ContentFile.subCategory.in_(sub_categories))

        blocks = query.all()

        # Подсчитываем компании
        company_counts = {}
        for block in blocks:
            if block.companies:
                for company in block.companies:
                    company_counts[company] = company_counts.get(company, 0) + 1

        companies = [
            TaskCompany(name=name, count=count)
            for name, count in sorted(company_counts.items())
        ]

        return companies

    # Методы для работы с TaskAttempt и TaskSolution

    async def create_task_attempt(self, user_id: int, **attempt_data) -> TaskAttempt:
        """Создание попытки решения задачи"""

        attempt = TaskAttempt(
            id=str(uuid4()),
            userId=user_id,
            createdAt=datetime.utcnow(),
            updatedAt=datetime.utcnow(),
            **attempt_data,
        )

        try:
            self.session.add(attempt)
            self.session.commit()
            self.session.refresh(attempt)
            return attempt
        except Exception as e:
            self.session.rollback()
            raise TaskAttemptError(f"Ошибка при создании попытки: {str(e)}")

    async def create_task_solution(self, user_id: int, **solution_data) -> TaskSolution:
        """Создание решения задачи"""

        solution = TaskSolution(
            id=str(uuid4()),
            userId=user_id,
            createdAt=datetime.utcnow(),
            updatedAt=datetime.utcnow(),
            **solution_data,
        )

        try:
            self.session.add(solution)
            self.session.commit()
            self.session.refresh(solution)
            return solution
        except Exception as e:
            self.session.rollback()
            raise TaskSolutionError(f"Ошибка при создании решения: {str(e)}")

    async def get_user_task_attempts(
        self, user_id: int, block_id: Optional[str] = None
    ) -> List[TaskAttempt]:
        """Получение попыток пользователя"""

        query = self.session.query(TaskAttempt).filter(TaskAttempt.userId == user_id)

        if block_id:
            query = query.filter(TaskAttempt.blockId == block_id)

        return query.order_by(TaskAttempt.createdAt.desc()).all()

    async def get_user_task_solutions(
        self, user_id: int, block_id: Optional[str] = None
    ) -> List[TaskSolution]:
        """Получение решений пользователя"""

        query = self.session.query(TaskSolution).filter(TaskSolution.userId == user_id)

        if block_id:
            query = query.filter(TaskSolution.blockId == block_id)

        return query.order_by(TaskSolution.solvedAt.desc()).all()

    def _unescape_text_content(self, text):
        if text is None:
            return None
        return html.unescape(text)

    def _sort_tasks(self, tasks, sort_by, sort_order):
        reverse = sort_order.lower() == "desc"

        def sort_key(t):
            value = t.get(sort_by) if isinstance(t, dict) else getattr(t, sort_by, None)
            return (value is None, value)

        return sorted(tasks, key=sort_key, reverse=reverse)
