"""
Progress Service - бизнес-логика для работы с прогрессом пользователей
"""

from datetime import datetime, timedelta
from typing import List, Optional

from app.core.logging import get_logger
from app.shared.database.base import transactional

from ..dto.requests import (
    CategoryProgressUpdateRequest,
    ContentProgressUpdateRequest,
    ProgressAnalyticsRequest,
)
from ..repositories.progress_repository import ProgressRepository

# Временные импорты TaskAttempt из task feature для обратной совместимости
try:
    from app.features.task.dto.requests import (
        TaskAttemptCreateRequest,
        TaskSolutionCreateRequest,
    )
    from app.features.task.dto.responses import (
        TaskAttemptResponse,
        TaskSolutionResponse,
    )
except ImportError:
    # Заглушки если task feature недоступна
    TaskAttemptCreateRequest = None
    TaskSolutionCreateRequest = None
    TaskAttemptResponse = None
    TaskSolutionResponse = None

from ..dto.responses import (
    AttemptHistoryResponse,
    CategoryProgressResponse,
    CategoryProgressSummaryResponse,
    ContentProgressResponse,
    GroupedCategoryProgressResponse,
    ProgressAnalyticsResponse,
    ProgressStatsResponse,
    RecentActivityResponse,
    UserDetailedProgressResponse,
    UserProgressSummaryResponse,
)

logger = get_logger(__name__)


class ProgressService:
    """Сервис для управления прогрессом пользователей"""

    def __init__(self, progress_repository: ProgressRepository):
        self.progress_repository = progress_repository

    # === Task Attempts ===

    @transactional
    async def create_task_attempt(
        self, request: TaskAttemptCreateRequest
    ) -> TaskAttemptResponse:
        """Создание попытки решения задачи"""
        logger.info(
            "Creating task attempt",
            extra={
                "user_id": request.user_id,
                "task_id": request.task_id,
                "is_successful": request.is_successful,
            },
        )

        try:
            # Создаем попытку
            attempt = await self.progress_repository.create_task_attempt(
                user_id=request.user_id,
                task_id=request.task_id,
                source_code=request.source_code,
                language=request.language,
                is_successful=request.is_successful,
                execution_time_ms=request.execution_time_ms,
                memory_used_mb=request.memory_used_mb,
                error_message=request.error_message,
                stderr=request.stderr,
                metadata=request.metadata,
            )

            # Если попытка успешна, создаем или обновляем решение
            if request.is_successful and request.source_code:
                await self._handle_successful_attempt(request, attempt.id)

            # Синхронизируем прогресс по контенту
            await self.progress_repository.sync_user_content_progress(
                user_id=request.user_id,
                block_id=request.task_id,
                is_successful=request.is_successful,
                time_spent=attempt.duration_minutes,
            )

            logger.info(
                "Task attempt created successfully",
                extra={
                    "attempt_id": attempt.id,
                    "user_id": request.user_id,
                    "task_id": request.task_id,
                },
            )

            return TaskAttemptResponse.model_validate(attempt)

        except Exception as e:
            logger.error(
                "Failed to create task attempt",
                extra={
                    "user_id": request.user_id,
                    "task_id": request.task_id,
                    "error": str(e),
                },
            )
            raise

    async def get_user_attempts(
        self, user_id: int, task_id: str = None, limit: int = 50
    ) -> List[TaskAttemptResponse]:
        """Получение попыток пользователя"""
        attempts = await self.progress_repository.get_user_attempts(
            user_id=user_id, task_id=task_id, limit=limit
        )

        return [TaskAttemptResponse.model_validate(attempt) for attempt in attempts]

    async def get_attempt_history(
        self, user_id: int, task_id: str
    ) -> AttemptHistoryResponse:
        """Получение истории попыток для задачи"""
        attempts = await self.progress_repository.get_attempt_history(user_id, task_id)
        solution = await self.progress_repository.get_task_solution(user_id, task_id)

        successful_attempts = [a for a in attempts if a.is_successful]
        best_time = (
            min(
                [
                    a.execution_time_ms
                    for a in successful_attempts
                    if a.execution_time_ms
                ]
            )
            if successful_attempts
            else None
        )
        first_success_attempt = (
            successful_attempts[0].attempt_number if successful_attempts else None
        )

        return AttemptHistoryResponse(
            task_id=task_id,
            user_id=user_id,
            attempts=[TaskAttemptResponse.model_validate(a) for a in attempts],
            total_attempts=len(attempts),
            successful_attempts=len(successful_attempts),
            best_time_ms=best_time,
            first_success_attempt=first_success_attempt,
            solution=TaskSolutionResponse.model_validate(solution)
            if solution
            else None,
        )

    # === Task Solutions ===

    @transactional
    async def create_task_solution(
        self, request: TaskSolutionCreateRequest
    ) -> TaskSolutionResponse:
        """Создание решения задачи"""
        logger.info(
            "Creating task solution",
            extra={"user_id": request.user_id, "task_id": request.task_id},
        )

        solution = await self.progress_repository.create_or_update_solution(
            user_id=request.user_id,
            task_id=request.task_id,
            source_code=request.source_code,
            language=request.language,
            execution_time_ms=request.execution_time_ms,
            memory_used_mb=request.memory_used_mb,
            is_optimal=request.is_optimal,
            solution_rating=request.solution_rating,
            metadata=request.metadata,
        )

        return TaskSolutionResponse.model_validate(solution)

    async def get_user_solutions(
        self, user_id: int, limit: int = 50
    ) -> List[TaskSolutionResponse]:
        """Получение решений пользователя"""
        solutions = await self.progress_repository.get_user_solutions(user_id, limit)
        return [TaskSolutionResponse.model_validate(solution) for solution in solutions]

    async def get_task_solution(
        self, user_id: int, task_id: str
    ) -> Optional[TaskSolutionResponse]:
        """Получение решения задачи"""
        solution = await self.progress_repository.get_task_solution(user_id, task_id)
        return TaskSolutionResponse.model_validate(solution) if solution else None

    # === Content Progress ===

    @transactional
    async def update_content_progress(
        self, request: ContentProgressUpdateRequest
    ) -> ContentProgressResponse:
        """Обновление прогресса по контенту"""
        progress = await self.progress_repository.sync_user_content_progress(
            user_id=request.user_id,
            block_id=request.block_id,
            is_successful=request.is_completed or False,
            time_spent=request.time_spent_minutes,
        )

        return ContentProgressResponse.model_validate(progress)

    async def get_user_content_progress(
        self, user_id: int, block_id: str = None
    ) -> List[ContentProgressResponse]:
        """Получение прогресса по контенту"""
        progress_list = await self.progress_repository.get_user_content_progress(
            user_id=user_id, block_id=block_id
        )

        return [
            ContentProgressResponse.model_validate(progress)
            for progress in progress_list
        ]

    # === Category Progress ===

    @transactional
    async def update_category_progress(
        self, request: CategoryProgressUpdateRequest
    ) -> CategoryProgressResponse:
        """Обновление прогресса по категории"""
        progress = await self.progress_repository.update_category_progress(
            user_id=request.user_id,
            main_category=request.main_category,
            sub_category=request.sub_category,
            total_tasks=request.total_tasks,
            completed_tasks=request.completed_tasks,
            attempted_tasks=request.attempted_tasks,
            time_spent=request.time_spent_minutes,
        )

        return CategoryProgressResponse.model_validate(progress)

    async def get_category_progress(
        self, user_id: int, main_category: str = None
    ) -> List[CategoryProgressResponse]:
        """Получение прогресса по категориям"""
        progress_list = await self.progress_repository.get_category_progress(
            user_id=user_id, main_category=main_category
        )

        return [
            CategoryProgressResponse.model_validate(progress)
            for progress in progress_list
        ]

    # === User Progress Summary ===

    async def get_user_progress_summary(
        self, user_id: int
    ) -> UserProgressSummaryResponse:
        """Получение сводки прогресса пользователя"""
        stats = await self.progress_repository.get_user_overall_stats(user_id)

        # TODO: Добавить вычисление streak и других метрик
        current_streak = 0
        longest_streak = 0
        registration_date = datetime.utcnow()  # Получить из User модели

        return UserProgressSummaryResponse(
            user_id=user_id,
            total_tasks_solved=stats["total_tasks_solved"],
            total_attempts=stats["total_attempts"],
            total_time_spent_minutes=stats["total_time_spent_minutes"],
            overall_success_rate=stats["overall_success_rate"],
            categories_started=stats["categories_started"],
            categories_completed=stats["categories_completed"],
            current_streak=current_streak,
            longest_streak=longest_streak,
            last_activity=stats["last_activity"],
            registration_date=registration_date,
        )

    async def get_user_detailed_progress(
        self, user_id: int
    ) -> UserDetailedProgressResponse:
        """Получение детального прогресса пользователя"""
        # Сводка пользователя
        user_summary = await self.get_user_progress_summary(user_id)

        # Прогресс по категориям
        category_progress = await self.get_category_progress(user_id)

        # Группированные категории
        grouped_categories = self._group_categories(category_progress)

        # Недавняя активность
        recent_activity_data = await self.progress_repository.get_recent_activity(
            user_id=user_id, limit=10
        )
        recent_activity = [
            RecentActivityResponse(**activity) for activity in recent_activity_data
        ]

        # TODO: Достижения и рекомендации
        achievements = []
        recommendations = []

        return UserDetailedProgressResponse(
            user_summary=user_summary,
            category_progress=category_progress,
            grouped_categories=grouped_categories,
            recent_activity=recent_activity,
            achievements=achievements,
            recommendations=recommendations,
        )

    # === Analytics ===

    async def get_progress_analytics(
        self, request: ProgressAnalyticsRequest
    ) -> ProgressAnalyticsResponse:
        """Получение аналитики прогресса"""
        analytics = await self.progress_repository.get_progress_analytics(
            user_id=request.user_id,
            date_from=request.date_from,
            date_to=request.date_to,
        )

        # TODO: Добавить популярные категории и сложные задачи
        most_popular_categories = []
        most_difficult_tasks = []

        return ProgressAnalyticsResponse(
            total_users=analytics["total_users"],
            active_users_today=analytics["active_users_today"],
            active_users_week=analytics["active_users_week"],
            total_tasks_solved=analytics["total_tasks_solved"],
            total_attempts=analytics["total_attempts"],
            average_success_rate=analytics["average_success_rate"],
            most_popular_categories=most_popular_categories,
            most_difficult_tasks=most_difficult_tasks,
            generated_at=analytics["generated_at"],
        )

    async def get_recent_activity(
        self, user_id: int = None, limit: int = 20
    ) -> List[RecentActivityResponse]:
        """Получение недавней активности"""
        activity_data = await self.progress_repository.get_recent_activity(
            user_id=user_id, limit=limit
        )

        return [RecentActivityResponse(**activity) for activity in activity_data]

    # === Progress Statistics ===

    async def get_progress_stats(
        self, user_id: int, period: str = "week"
    ) -> ProgressStatsResponse:
        """Получение статистики прогресса за период"""
        # Определяем период
        if period == "day":
            date_from = datetime.utcnow() - timedelta(days=1)
        elif period == "week":
            date_from = datetime.utcnow() - timedelta(days=7)
        elif period == "month":
            date_from = datetime.utcnow() - timedelta(days=30)
        else:
            date_from = datetime.utcnow() - timedelta(days=7)

        # Получаем аналитику за период
        request = ProgressAnalyticsRequest(
            user_id=user_id, date_from=date_from, date_to=datetime.utcnow()
        )

        analytics = await self.get_progress_analytics(request)

        # TODO: Добавить вычисление improvement_rate, streak_days, categories_active
        improvement_rate = None
        streak_days = 0
        categories_active = 0

        return ProgressStatsResponse(
            period=period,
            tasks_solved=analytics.total_tasks_solved,
            time_spent_hours=0.0,  # Вычислить из данных
            success_rate=analytics.average_success_rate,
            improvement_rate=improvement_rate,
            streak_days=streak_days,
            categories_active=categories_active,
        )

    # === Private Methods ===

    async def _handle_successful_attempt(
        self, request: TaskAttemptCreateRequest, attempt_id: str
    ) -> None:
        """Обработка успешной попытки"""
        # Создаем или обновляем решение
        await self.progress_repository.create_or_update_solution(
            user_id=request.user_id,
            task_id=request.task_id,
            source_code=request.source_code,
            language=request.language,
            execution_time_ms=request.execution_time_ms,
            memory_used_mb=request.memory_used_mb,
            attempt_id=attempt_id,
            metadata=request.metadata,
        )

        # TODO: Обновить общую статистику пользователя
        # TODO: Обновить прогресс по категориям
        # TODO: Проверить достижения

    def _group_categories(
        self, category_progress: List[CategoryProgressResponse]
    ) -> List[GroupedCategoryProgressResponse]:
        """Группировка прогресса по основным категориям"""
        grouped = {}

        for progress in category_progress:
            main_cat = progress.main_category

            if main_cat not in grouped:
                grouped[main_cat] = {
                    "main_category": main_cat,
                    "total_completed": 0,
                    "total_tasks": 0,
                    "sub_categories": [],
                    "last_activity": None,
                }

            # Добавляем к общим метрикам
            grouped[main_cat]["total_completed"] += progress.completed_tasks
            grouped[main_cat]["total_tasks"] += progress.total_tasks

            # Обновляем последнюю активность
            if not grouped[main_cat]["last_activity"] or (
                progress.last_activity
                and progress.last_activity > grouped[main_cat]["last_activity"]
            ):
                grouped[main_cat]["last_activity"] = progress.last_activity

            # Добавляем подкатегорию
            sub_category = CategoryProgressSummaryResponse(
                main_category=progress.main_category,
                sub_category=progress.sub_category,
                completed_tasks=progress.completed_tasks,
                total_tasks=progress.total_tasks,
                completion_percentage=progress.completion_percentage,
                status=progress.status,
                last_activity=progress.last_activity,
            )
            grouped[main_cat]["sub_categories"].append(sub_category)

        # Преобразуем в список ответов
        result = []
        for main_cat, data in grouped.items():
            overall_completion = (
                (data["total_completed"] / data["total_tasks"] * 100)
                if data["total_tasks"] > 0
                else 0
            )

            result.append(
                GroupedCategoryProgressResponse(
                    main_category=main_cat,
                    total_completed=data["total_completed"],
                    total_tasks=data["total_tasks"],
                    overall_completion_percentage=overall_completion,
                    sub_categories=data["sub_categories"],
                    last_activity=data["last_activity"],
                )
            )

        return result
