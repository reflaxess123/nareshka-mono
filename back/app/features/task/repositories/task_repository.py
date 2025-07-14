"""Репозиторий для работы с заданиями"""

from typing import List, Optional, Tuple
from uuid import uuid4
from datetime import datetime

from sqlalchemy import asc, func, or_
from sqlalchemy.orm import Session, joinedload

from app.shared.entities.task_types import Task
from app.features.task.dto.responses import TaskCategoryResponse as TaskCategory, TaskCompanyResponse as TaskCompany
from app.shared.models.content_models import (
    ContentBlock,
    ContentFile,
)
from app.shared.models.content_models import UserContentProgress
from app.shared.models.theory_models import TheoryCard, UserTheoryProgress
from app.shared.models.task_models import TaskAttempt, TaskSolution
from app.features.task.exceptions.task_exceptions import (
    TaskNotFoundError,
    TaskAttemptError,
    TaskSolutionError,
)


class TaskRepository:
    """Репозиторий для работы с заданиями"""

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
                sort_key = task.createdAt
            elif sort_by == "updatedAt":
                sort_key = task.updatedAt
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

        # Получаем прогресс пользователя
        user_progress = {}
        if user_id:
            progress_records = (
                self.session.query(UserContentProgress)
                .filter(UserContentProgress.userId == user_id)
                .all()
            )
            user_progress = {p.blockId: p.solvedCount for p in progress_records}

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
            
            task = Task(
                id=block.id,
                item_type="content_block",
                title=block.file.webdavPath.split("/")[-1] if block.file else "Без названия",
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
                current_user_solved_count=user_progress.get(block.id, 0),
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
    
    async def create_task_attempt(
        self, user_id: int, **attempt_data
    ) -> TaskAttempt:
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

    async def create_task_solution(
        self, user_id: int, **solution_data
    ) -> TaskSolution:
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



