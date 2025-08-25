"""
Progress Repository - репозиторий для работы с прогрессом пользователей
"""

import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, asc, desc, func, text, case
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.features.progress.utils.constants import TIME_MS_TO_MINUTES, ACTIVITY_TYPE_TASK_ATTEMPTED, ACTIVITY_TYPE_TASK_SOLVED
from app.shared.database import BaseRepository, transactional
from app.shared.database.connection import SessionLocal
from app.shared.models.content_models import UserContentProgress
from app.shared.models.progress_models import UserCategoryProgress
from app.shared.models.task_models import TaskAttempt, TaskSolution

logger = get_logger(__name__)


class ProgressRepository(BaseRepository[UserCategoryProgress]):
    """
    Repository для работы с прогрессом пользователей
    """

    def __init__(self):
        super().__init__(UserCategoryProgress)

    # === Task Attempts ===

    @transactional
    async def create_task_attempt(
        self,
        user_id: int,
        task_id: str,
        source_code: str = None,
        language: str = None,
        is_successful: bool = False,
        execution_time_ms: int = None,
        memory_used_mb: Decimal = None,
        error_message: str = None,
        stderr: str = None,
        metadata: Dict[str, Any] = None,
        session: Session = None,
    ) -> TaskAttempt:
        """Создание попытки решения задачи"""

        # Получаем номер попытки
        attempt_number = await self.get_next_attempt_number(user_id, task_id, session)

        attempt = TaskAttempt(
            id=str(uuid.uuid4()),
            userId=user_id,
            blockId=task_id,
            sourceCode=source_code,
            language=language,
            isSuccessful=is_successful,
            executionTimeMs=execution_time_ms,
            memoryUsedMB=memory_used_mb,
            errorMessage=error_message,
            stderr=stderr,
            attemptNumber=attempt_number,
        )

        session.add(attempt)
        session.flush()

        logger.info(
            "Task attempt created",
            extra={
                "user_id": user_id,
                "task_id": task_id,
                "attempt_id": attempt.id,
                "is_successful": is_successful,
                "attempt_number": attempt_number,
            },
        )

        return attempt

    async def get_next_attempt_number(
        self, user_id: int, task_id: str, session: Session = None
    ) -> int:
        """Получение номера следующей попытки"""
        if session is None:
            with SessionLocal() as session:
                max_attempt = (
                    session.query(func.max(TaskAttempt.attemptNumber))
                    .filter(
                        and_(TaskAttempt.userId == user_id, TaskAttempt.blockId == task_id)
                    )
                    .scalar()
                )
                return (max_attempt or 0) + 1
        else:
            max_attempt = (
                session.query(func.max(TaskAttempt.attemptNumber))
                .filter(
                    and_(TaskAttempt.userId == user_id, TaskAttempt.blockId == task_id)
                )
                .scalar()
            )
            return (max_attempt or 0) + 1

    async def get_user_attempts(
        self,
        user_id: int,
        task_id: str = None,
        limit: int = 50,
        session: Session = None,
    ) -> List[TaskAttempt]:
        """Получение попыток пользователя"""
        if session is None:
            with SessionLocal() as session:
                query = session.query(TaskAttempt).filter(TaskAttempt.userId == user_id)
                if task_id:
                    query = query.filter(TaskAttempt.blockId == task_id)
                return query.order_by(desc(TaskAttempt.createdAt)).limit(limit).all()
        else:
            query = session.query(TaskAttempt).filter(TaskAttempt.userId == user_id)
            if task_id:
                query = query.filter(TaskAttempt.blockId == task_id)
            return query.order_by(desc(TaskAttempt.createdAt)).limit(limit).all()

    async def get_attempt_history(
        self, user_id: int, task_id: str, session: Session = None
    ) -> List[TaskAttempt]:
        """Получение истории попыток для конкретной задачи"""
        if session is None:
            with SessionLocal() as session:
                return (
                    session.query(TaskAttempt)
                    .filter(
                        and_(TaskAttempt.userId == user_id, TaskAttempt.blockId == task_id)
                    )
                    .order_by(asc(TaskAttempt.attemptNumber))
                    .all()
                )
        else:
            return (
                session.query(TaskAttempt)
                .filter(
                    and_(TaskAttempt.userId == user_id, TaskAttempt.blockId == task_id)
                )
                .order_by(asc(TaskAttempt.attemptNumber))
                .all()
            )

    # === Task Solutions ===

    @transactional
    async def create_or_update_solution(
        self,
        user_id: int,
        task_id: str,
        source_code: str,
        language: str,
        execution_time_ms: int = None,
        memory_used_mb: Decimal = None,
        attempt_id: str = None,
        is_optimal: bool = False,
        solution_rating: int = None,
        metadata: Dict[str, Any] = None,
        session: Session = None,
    ) -> TaskSolution:
        """Создание или обновление решения задачи"""

        # Проверяем существующее решение
        existing_solution = (
            session.query(TaskSolution)
            .filter(
                and_(TaskSolution.userId == user_id, TaskSolution.blockId == task_id)
            )
            .first()
        )

        if existing_solution:
            # Обновляем существующее решение
            existing_solution.finalCode = source_code
            existing_solution.language = language
            existing_solution.totalAttempts += 1

            logger.info(
                "Task solution updated",
                extra={
                    "user_id": user_id,
                    "task_id": task_id,
                    "solution_id": existing_solution.id,
                },
            )

            return existing_solution

        else:
            # Создаем новое решение
            solution = TaskSolution(
                id=str(uuid.uuid4()),
                userId=user_id,
                blockId=task_id,
                finalCode=source_code,
                language=language,
                totalAttempts=1,
                timeToSolveMinutes=execution_time_ms // (1000 * 60)
                if execution_time_ms
                else 0,
                firstAttempt=datetime.utcnow(),
            )

            session.add(solution)
            session.flush()

            logger.info(
                "Task solution created",
                extra={
                    "user_id": user_id,
                    "task_id": task_id,
                    "solution_id": solution.id,
                },
            )

            return solution

    async def get_user_solutions(
        self, user_id: int, limit: int = 50, session: Session = None
    ) -> List[TaskSolution]:
        """Получение решений пользователя"""
        if session is None:
            with SessionLocal() as session:
                return (
                    session.query(TaskSolution)
                    .filter(TaskSolution.userId == user_id)
                    .order_by(desc(TaskSolution.createdAt))
                    .limit(limit)
                    .all()
                )
        else:
            return (
                session.query(TaskSolution)
                .filter(TaskSolution.userId == user_id)
                .order_by(desc(TaskSolution.createdAt))
                .limit(limit)
                .all()
            )

    async def get_task_solution(
        self, user_id: int, task_id: str, session: Session = None
    ) -> Optional[TaskSolution]:
        """Получение решения задачи"""
        if session is None:
            with SessionLocal() as session:
                return (
                    session.query(TaskSolution)
                    .filter(
                        and_(
                            TaskSolution.userId == user_id, TaskSolution.blockId == task_id
                        )
                    )
                    .first()
                )
        else:
            return (
                session.query(TaskSolution)
                .filter(
                    and_(
                        TaskSolution.userId == user_id, TaskSolution.blockId == task_id
                    )
                )
                .first()
            )

    # === Content Progress ===

    @transactional
    async def sync_user_content_progress(
        self,
        user_id: int,
        block_id: str,
        is_successful: bool = False,
        time_spent: int = None,
        session: Session = None,
    ) -> UserContentProgress:
        """Синхронизация прогресса по контенту"""

        # Получаем или создаем запись прогресса
        progress = (
            session.query(UserContentProgress)
            .filter(
                and_(
                    UserContentProgress.userId == user_id,
                    UserContentProgress.blockId == block_id,
                )
            )
            .first()
        )

        if not progress:
            progress = UserContentProgress(
                id=str(uuid.uuid4()), userId=user_id, blockId=block_id, solvedCount=0
            )
            session.add(progress)

        # Обновляем прогресс
        if is_successful:
            progress.solvedCount += 1

        logger.info(
            "Content progress synced",
            extra={
                "user_id": user_id,
                "block_id": block_id,
                "is_successful": is_successful,
                "progress_id": progress.id,
            },
        )

        return progress

    async def get_user_content_progress(
        self, user_id: int, block_id: str = None, session: Session = None
    ) -> List[UserContentProgress]:
        """Получение прогресса по контенту"""
        if session is None:
            with SessionLocal() as session:
                query = session.query(UserContentProgress).filter(
                    UserContentProgress.userId == user_id
                )
                if block_id:
                    query = query.filter(UserContentProgress.blockId == block_id)
                return query.order_by(desc(UserContentProgress.updatedAt)).all()
        else:
            query = session.query(UserContentProgress).filter(
                UserContentProgress.userId == user_id
            )
            if block_id:
                query = query.filter(UserContentProgress.blockId == block_id)
            return query.order_by(desc(UserContentProgress.updatedAt)).all()

    # === Category Progress ===

    @transactional
    async def update_category_progress(
        self,
        user_id: int,
        main_category: str,
        sub_category: str = None,
        total_tasks: int = None,
        completed_tasks: int = None,
        attempted_tasks: int = None,
        time_spent: int = None,
        session: Session = None,
    ) -> UserCategoryProgress:
        """Обновление прогресса по категории"""

        # Получаем или создаем запись прогресса
        progress = (
            session.query(UserCategoryProgress)
            .filter(
                and_(
                    UserCategoryProgress.userId == user_id,
                    UserCategoryProgress.mainCategory == main_category,
                    UserCategoryProgress.subCategory == sub_category,
                )
            )
            .first()
        )

        if not progress:
            progress = UserCategoryProgress(
                id=str(uuid.uuid4()),
                userId=user_id,
                mainCategory=main_category,
                subCategory=sub_category,
                totalTasks=0,
                completedTasks=0,
                attemptedTasks=0,
            )
            session.add(progress)
            session.flush()

        # Устанавливаем первую попытку если её еще нет
        if not progress.firstAttempt:
            progress.firstAttempt = datetime.utcnow()

        # Обновляем метрики
        if total_tasks is not None:
            progress.totalTasks = total_tasks
        if completed_tasks is not None:
            progress.completedTasks = completed_tasks
        if attempted_tasks is not None:
            progress.attemptedTasks = attempted_tasks
        if time_spent is not None:
            progress.totalTimeSpentMinutes = (
                progress.totalTimeSpentMinutes or 0
            ) + time_spent

        # Обновляем последнюю активность
        progress.lastActivity = datetime.utcnow()

        # Пересчитываем коэффициенты
        if progress.attemptedTasks > 0:
            progress.successRate = Decimal(
                str((progress.completedTasks / progress.attemptedTasks) * 100)
            )

        if progress.completedTasks > 0:
            progress.averageAttempts = Decimal(
                str(progress.attemptedTasks / progress.completedTasks)
            )

        logger.info(
            "Category progress updated",
            extra={
                "user_id": user_id,
                "main_category": main_category,
                "sub_category": sub_category,
                "progress_id": progress.id,
            },
        )

        return progress

    async def get_category_progress(
        self, user_id: int, main_category: str = None, session: Session = None
    ) -> List[UserCategoryProgress]:
        """Получение прогресса по категориям"""
        if session is None:
            with SessionLocal() as session:
                query = session.query(UserCategoryProgress).filter(
                    UserCategoryProgress.userId == user_id
                )
                if main_category:
                    query = query.filter(UserCategoryProgress.mainCategory == main_category)
                return query.order_by(
                    UserCategoryProgress.mainCategory, UserCategoryProgress.subCategory
                ).all()
        else:
            query = session.query(UserCategoryProgress).filter(
                UserCategoryProgress.userId == user_id
            )
            if main_category:
                query = query.filter(UserCategoryProgress.mainCategory == main_category)
            return query.order_by(
                UserCategoryProgress.mainCategory, UserCategoryProgress.subCategory
            ).all()

    # === Analytics ===

    async def get_user_overall_stats(
        self, user_id: int, session: Session = None
    ) -> Dict[str, Any]:
        """Получение общей статистики пользователя"""
        if session is None:
            with SessionLocal() as session:
                return await self._get_user_stats_query(session, user_id)
        else:
            return await self._get_user_stats_query(session, user_id)
    
    async def _get_user_stats_query(self, session: Session, user_id: int) -> Dict[str, Any]:
        """Оптимизированный запрос статистики одним SQL"""
        # Объединяем все статистики в один запрос
        result = (
            session.query(
                # Attempts stats
                func.count(TaskAttempt.id).label("total_attempts"),
                func.sum(
                    case((TaskAttempt.isSuccessful.is_(True), 1), else_=0)
                ).label("successful_attempts"),
                func.sum(TaskAttempt.executionTimeMs).label("total_time_ms"),
                func.max(TaskAttempt.createdAt).label("last_activity"),
                # Solutions count (subquery)
                session.query(func.count(TaskSolution.id))
                .filter(TaskSolution.userId == user_id)
                .label("solution_count"),
                # Categories stats (subquery)
                session.query(func.count(UserCategoryProgress.id))
                .filter(UserCategoryProgress.userId == user_id)
                .label("categories_started"),
                session.query(
                    func.count(UserCategoryProgress.id)
                ).filter(
                    and_(
                        UserCategoryProgress.userId == user_id,
                        UserCategoryProgress.completedTasks >= UserCategoryProgress.totalTasks
                    )
                ).label("categories_completed"),
            )
            .filter(TaskAttempt.userId == user_id)
            .first()
        )

        total_attempts = result.total_attempts or 0
        successful_attempts = result.successful_attempts or 0
        TIME_MS_TO_MINUTES = 1000 * 60

        return {
            "user_id": user_id,
            "total_tasks_solved": result.solution_count or 0,
            "total_attempts": total_attempts,
            "successful_attempts": successful_attempts,
            "total_time_spent_minutes": (result.total_time_ms or 0) // TIME_MS_TO_MINUTES,
            "overall_success_rate": Decimal(
                str(
                    (successful_attempts / total_attempts * 100)
                    if total_attempts > 0
                    else 0
                )
            ),
            "categories_started": result.categories_started or 0,
            "categories_completed": result.categories_completed or 0,
            "last_activity": result.last_activity,
        }

    async def get_progress_analytics(
        self,
        user_id: int = None,
        date_from: datetime = None,
        date_to: datetime = None,
        session: Session = None,
    ) -> Dict[str, Any]:
        """Получение аналитики прогресса"""
        if session is None:
            with SessionLocal() as session:
                return await self._get_analytics_query(session, user_id, date_from, date_to)
        else:
            return await self._get_analytics_query(session, user_id, date_from, date_to)
    
    async def _get_analytics_query(
        self, session: Session, user_id: int, date_from: datetime, date_to: datetime
    ) -> Dict[str, Any]:
        """Оптимизированный запрос аналитики"""
        query_filter = []
        if user_id:
            query_filter.append(TaskAttempt.userId == user_id)
        if date_from:
            query_filter.append(TaskAttempt.createdAt >= date_from)
        if date_to:
            query_filter.append(TaskAttempt.createdAt <= date_to)

        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=7)
        
        # Объединяем все в один запрос через CTE
        base_filter = and_(*query_filter) if query_filter else text("1=1")
        
        result = (
            session.query(
                # Основная статистика
                func.count(func.distinct(TaskAttempt.userId)).label("total_users"),
                func.count(TaskAttempt.id).label("total_attempts"),
                func.sum(
                    case((TaskAttempt.isSuccessful.is_(True), 1), else_=0)
                ).label("successful_attempts"),
                # Активные пользователи сегодня
                func.count(
                    func.distinct(
                        case(
                            (func.date(TaskAttempt.createdAt) == today, TaskAttempt.userId),
                            else_=None
                        )
                    )
                ).label("active_users_today"),
                # Активные пользователи за неделю
                func.count(
                    func.distinct(
                        case(
                            (func.date(TaskAttempt.createdAt) >= week_ago, TaskAttempt.userId),
                            else_=None
                        )
                    )
                ).label("active_users_week"),
            )
            .filter(base_filter)
            .first()
        )

        total_attempts = result.total_attempts or 0
        successful_attempts = result.successful_attempts or 0

        return {
            "total_users": result.total_users or 0,
            "active_users_today": result.active_users_today or 0,
            "active_users_week": result.active_users_week or 0,
            "total_attempts": total_attempts,
            "total_tasks_solved": successful_attempts,
            "average_success_rate": Decimal(
                str(
                    (successful_attempts / total_attempts * 100)
                    if total_attempts > 0
                    else 0
                )
            ),
            "generated_at": datetime.utcnow(),
        }

    async def get_recent_activity(
        self, user_id: int = None, limit: int = 20, session: Session = None
    ) -> List[Dict[str, Any]]:
        """Получение недавней активности"""
        if session is None:
            with SessionLocal() as session:
                return await self._get_recent_activity_query(session, user_id, limit)
        else:
            return await self._get_recent_activity_query(session, user_id, limit)
    
    async def _get_recent_activity_query(
        self, session: Session, user_id: int, limit: int
    ) -> List[Dict[str, Any]]:
        """Оптимизированный запрос активности"""
        query = session.query(TaskAttempt)
        if user_id:
            query = query.filter(TaskAttempt.userId == user_id)
        
        attempts = query.order_by(desc(TaskAttempt.createdAt)).limit(limit).all()
        
        return [
            {
                "user_id": attempt.userId,
                "activity_type": ACTIVITY_TYPE_TASK_SOLVED if attempt.isSuccessful else ACTIVITY_TYPE_TASK_ATTEMPTED,
                "description": f"{'Решена' if attempt.isSuccessful else 'Попытка решения'} задача {attempt.blockId}",
                "task_id": attempt.blockId,
                "timestamp": attempt.createdAt,
                "metadata": {
                    "language": attempt.language,
                    "execution_time_ms": attempt.executionTimeMs,
                    "is_successful": attempt.isSuccessful,
                },
            }
            for attempt in attempts
        ]
