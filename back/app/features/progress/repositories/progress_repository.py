"""
Progress Repository - репозиторий для работы с прогрессом пользователей
"""

import uuid
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import and_, or_, func, desc, asc, text
from sqlalchemy.orm import Session

from app.shared.database import BaseRepository, transactional, get_session
from app.shared.exceptions.base import ResourceNotFoundException, ConflictError
from app.core.logging import get_logger

from app.shared.models.enums import ProgressStatus
from app.shared.models.progress_models import UserCategoryProgress
from app.shared.models.content_models import UserContentProgress
# TaskAttempt и TaskSolution теперь в task feature
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
        session: Session = None
    ) -> TaskAttempt:
        """Создание попытки решения задачи"""
        
        # Получаем номер попытки
        attempt_number = await self.get_next_attempt_number(user_id, task_id, session)
        
        attempt = TaskAttempt(
            id=str(uuid.uuid4()),
            user_id=user_id,
            task_id=task_id,
            source_code=source_code,
            language=language,
            result=AttemptResult.SUCCESS if is_successful else AttemptResult.FAILED,
            is_successful=is_successful,
            execution_time_ms=execution_time_ms,
            memory_used_mb=memory_used_mb,
            error_message=error_message,
            stderr=stderr,
            attempt_number=attempt_number,
            metadata=metadata or {}
        )
        
        session.add(attempt)
        session.flush()
        
        logger.info("Task attempt created", extra={
            "user_id": user_id,
            "task_id": task_id,
            "attempt_id": attempt.id,
            "is_successful": is_successful,
            "attempt_number": attempt_number
        })
        
        return attempt
    
    async def get_next_attempt_number(
        self, 
        user_id: int, 
        task_id: str,
        session: Session = None
    ) -> int:
        """Получение номера следующей попытки"""
        if session is None:
            session = get_session()
        
        max_attempt = session.query(func.max(TaskAttempt.attempt_number)).filter(
            and_(
                TaskAttempt.user_id == user_id,
                TaskAttempt.task_id == task_id
            )
        ).scalar()
        
        return (max_attempt or 0) + 1
    
    async def get_user_attempts(
        self, 
        user_id: int,
        task_id: str = None,
        limit: int = 50,
        session: Session = None
    ) -> List[TaskAttempt]:
        """Получение попыток пользователя"""
        if session is None:
            session = get_session()
        
        query = session.query(TaskAttempt).filter(TaskAttempt.user_id == user_id)
        
        if task_id:
            query = query.filter(TaskAttempt.task_id == task_id)
        
        return query.order_by(desc(TaskAttempt.created_at)).limit(limit).all()
    
    async def get_attempt_history(
        self, 
        user_id: int, 
        task_id: str,
        session: Session = None
    ) -> List[TaskAttempt]:
        """Получение истории попыток для конкретной задачи"""
        if session is None:
            session = get_session()
        
        return session.query(TaskAttempt).filter(
            and_(
                TaskAttempt.user_id == user_id,
                TaskAttempt.task_id == task_id
            )
        ).order_by(asc(TaskAttempt.attempt_number)).all()
    
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
        session: Session = None
    ) -> TaskSolution:
        """Создание или обновление решения задачи"""
        
        # Проверяем существующее решение
        existing_solution = session.query(TaskSolution).filter(
            and_(
                TaskSolution.user_id == user_id,
                TaskSolution.task_id == task_id
            )
        ).first()
        
        if existing_solution:
            # Обновляем существующее решение
            existing_solution.source_code = source_code
            existing_solution.language = language
            existing_solution.total_attempts += 1
            existing_solution.attempt_id = attempt_id
            existing_solution.is_optimal = is_optimal
            existing_solution.solution_rating = solution_rating
            existing_solution.metadata = metadata or {}
            
            # Обновляем лучшие метрики
            if execution_time_ms:
                existing_solution.update_best_metrics(execution_time_ms, float(memory_used_mb or 0))
            
            logger.info("Task solution updated", extra={
                "user_id": user_id,
                "task_id": task_id,
                "solution_id": existing_solution.id
            })
            
            return existing_solution
        
        else:
            # Создаем новое решение
            solution = TaskSolution(
                id=str(uuid.uuid4()),
                user_id=user_id,
                task_id=task_id,
                source_code=source_code,
                language=language,
                best_execution_time_ms=execution_time_ms,
                best_memory_used_mb=memory_used_mb,
                total_attempts=1,
                attempt_id=attempt_id,
                is_optimal=is_optimal,
                solution_rating=solution_rating,
                metadata=metadata or {}
            )
            
            session.add(solution)
            session.flush()
            
            logger.info("Task solution created", extra={
                "user_id": user_id,
                "task_id": task_id,
                "solution_id": solution.id
            })
            
            return solution
    
    async def get_user_solutions(
        self, 
        user_id: int,
        limit: int = 50,
        session: Session = None
    ) -> List[TaskSolution]:
        """Получение решений пользователя"""
        if session is None:
            session = get_session()
        
        return session.query(TaskSolution).filter(
            TaskSolution.user_id == user_id
        ).order_by(desc(TaskSolution.created_at)).limit(limit).all()
    
    async def get_task_solution(
        self, 
        user_id: int, 
        task_id: str,
        session: Session = None
    ) -> Optional[TaskSolution]:
        """Получение решения задачи"""
        if session is None:
            session = get_session()
        
        return session.query(TaskSolution).filter(
            and_(
                TaskSolution.user_id == user_id,
                TaskSolution.task_id == task_id
            )
        ).first()
    
    # === Content Progress ===
    
    @transactional
    async def sync_user_content_progress(
        self,
        user_id: int,
        block_id: str,
        is_successful: bool = False,
        time_spent: int = None,
        session: Session = None
    ) -> UserContentProgress:
        """Синхронизация прогресса по контенту"""
        
        # Получаем или создаем запись прогресса
        progress = session.query(UserContentProgress).filter(
            and_(
                UserContentProgress.userId == user_id,
                UserContentProgress.blockId == block_id
            )
        ).first()
        
        if not progress:
            progress = UserContentProgress(
                id=str(uuid.uuid4()),
                userId=user_id,
                blockId=block_id,
                solvedCount=0,
                attempt_count=0,
                is_completed=False,
                status=ProgressStatus.NOT_STARTED
            )
            session.add(progress)
        
        # Обновляем прогресс
        progress.add_attempt(is_successful, time_spent)
        
        logger.info("Content progress synced", extra={
            "user_id": user_id,
            "block_id": block_id,
            "is_successful": is_successful,
            "progress_id": progress.id
        })
        
        return progress
    
    async def get_user_content_progress(
        self, 
        user_id: int,
        block_id: str = None,
        session: Session = None
    ) -> List[UserContentProgress]:
        """Получение прогресса по контенту"""
        if session is None:
            session = get_session()
        
        query = session.query(UserContentProgress).filter(
            UserContentProgress.userId == user_id
        )
        
        if block_id:
            query = query.filter(UserContentProgress.blockId == block_id)
        
        return query.order_by(desc(UserContentProgress.last_attempt_at)).all()
    
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
        session: Session = None
    ) -> UserCategoryProgress:
        """Обновление прогресса по категории"""
        
        # Получаем или создаем запись прогресса
        progress = session.query(UserCategoryProgress).filter(
            and_(
                UserCategoryProgress.user_id == user_id,
                UserCategoryProgress.main_category == main_category,
                UserCategoryProgress.sub_category == sub_category
            )
        ).first()
        
        if not progress:
            progress = UserCategoryProgress(
                id=str(uuid.uuid4()),
                user_id=user_id,
                main_category=main_category,
                sub_category=sub_category,
                total_tasks=0,
                completed_tasks=0,
                attempted_tasks=0
            )
            session.add(progress)
            session.flush()
        
        # Устанавливаем первую попытку если её еще нет
        if not progress.first_attempt:
            progress.first_attempt = datetime.utcnow()
        
        # Обновляем метрики
        if total_tasks is not None or completed_tasks is not None or attempted_tasks is not None:
            progress.update_metrics(
                total_tasks=total_tasks or progress.total_tasks,
                completed_tasks=completed_tasks or progress.completed_tasks,
                attempted_tasks=attempted_tasks or progress.attempted_tasks,
                time_spent=time_spent
            )
        
        logger.info("Category progress updated", extra={
            "user_id": user_id,
            "main_category": main_category,
            "sub_category": sub_category,
            "progress_id": progress.id
        })
        
        return progress
    
    async def get_category_progress(
        self, 
        user_id: int,
        main_category: str = None,
        session: Session = None
    ) -> List[UserCategoryProgress]:
        """Получение прогресса по категориям"""
        if session is None:
            session = get_session()
        
        query = session.query(UserCategoryProgress).filter(
            UserCategoryProgress.user_id == user_id
        )
        
        if main_category:
            query = query.filter(UserCategoryProgress.main_category == main_category)
        
        return query.order_by(
            UserCategoryProgress.main_category,
            UserCategoryProgress.sub_category
        ).all()
    
    # === Analytics ===
    
    async def get_user_overall_stats(
        self, 
        user_id: int,
        session: Session = None
    ) -> Dict[str, Any]:
        """Получение общей статистики пользователя"""
        if session is None:
            session = get_session()
        
        # Общая статистика попыток
        attempt_stats = session.query(
            func.count(TaskAttempt.id).label('total_attempts'),
            func.count(TaskAttempt.id).filter(TaskAttempt.is_successful == True).label('successful_attempts'),
            func.sum(TaskAttempt.execution_time_ms).label('total_time_ms')
        ).filter(TaskAttempt.user_id == user_id).first()
        
        # Статистика решений
        solution_count = session.query(func.count(TaskSolution.id)).filter(
            TaskSolution.user_id == user_id
        ).scalar() or 0
        
        # Статистика категорий
        category_stats = session.query(
            func.count(UserCategoryProgress.id).label('categories_started'),
            func.count(UserCategoryProgress.id).filter(
                UserCategoryProgress.status == ProgressStatus.COMPLETED
            ).label('categories_completed')
        ).filter(UserCategoryProgress.user_id == user_id).first()
        
        # Последняя активность
        last_activity = session.query(func.max(TaskAttempt.created_at)).filter(
            TaskAttempt.user_id == user_id
        ).scalar()
        
        total_attempts = attempt_stats.total_attempts or 0
        successful_attempts = attempt_stats.successful_attempts or 0
        
        return {
            'user_id': user_id,
            'total_tasks_solved': solution_count,
            'total_attempts': total_attempts,
            'successful_attempts': successful_attempts,
            'total_time_spent_minutes': (attempt_stats.total_time_ms or 0) // (1000 * 60),
            'overall_success_rate': Decimal(
                str((successful_attempts / total_attempts * 100) if total_attempts > 0 else 0)
            ),
            'categories_started': category_stats.categories_started or 0,
            'categories_completed': category_stats.categories_completed or 0,
            'last_activity': last_activity
        }
    
    async def get_progress_analytics(
        self, 
        user_id: int = None,
        date_from: datetime = None,
        date_to: datetime = None,
        session: Session = None
    ) -> Dict[str, Any]:
        """Получение аналитики прогресса"""
        if session is None:
            session = get_session()
        
        query_filter = []
        
        if user_id:
            query_filter.append(TaskAttempt.user_id == user_id)
        
        if date_from:
            query_filter.append(TaskAttempt.created_at >= date_from)
        
        if date_to:
            query_filter.append(TaskAttempt.created_at <= date_to)
        
        # Общая статистика
        stats = session.query(
            func.count(func.distinct(TaskAttempt.user_id)).label('total_users'),
            func.count(TaskAttempt.id).label('total_attempts'),
            func.count(TaskAttempt.id).filter(TaskAttempt.is_successful == True).label('successful_attempts')
        ).filter(and_(*query_filter) if query_filter else text('1=1')).first()
        
        # Активные пользователи
        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=7)
        
        active_today = session.query(func.count(func.distinct(TaskAttempt.user_id))).filter(
            and_(
                func.date(TaskAttempt.created_at) == today,
                *query_filter
            ) if query_filter else func.date(TaskAttempt.created_at) == today
        ).scalar() or 0
        
        active_week = session.query(func.count(func.distinct(TaskAttempt.user_id))).filter(
            and_(
                func.date(TaskAttempt.created_at) >= week_ago,
                *query_filter
            ) if query_filter else func.date(TaskAttempt.created_at) >= week_ago
        ).scalar() or 0
        
        total_attempts = stats.total_attempts or 0
        successful_attempts = stats.successful_attempts or 0
        
        return {
            'total_users': stats.total_users or 0,
            'active_users_today': active_today,
            'active_users_week': active_week,
            'total_attempts': total_attempts,
            'total_tasks_solved': successful_attempts,
            'average_success_rate': Decimal(
                str((successful_attempts / total_attempts * 100) if total_attempts > 0 else 0)
            ),
            'generated_at': datetime.utcnow()
        }
    
    async def get_recent_activity(
        self, 
        user_id: int = None,
        limit: int = 20,
        session: Session = None
    ) -> List[Dict[str, Any]]:
        """Получение недавней активности"""
        if session is None:
            session = get_session()
        
        query = session.query(TaskAttempt)
        
        if user_id:
            query = query.filter(TaskAttempt.user_id == user_id)
        
        attempts = query.order_by(desc(TaskAttempt.created_at)).limit(limit).all()
        
        activities = []
        for attempt in attempts:
            activity_type = "task_solved" if attempt.is_successful else "task_attempted"
            description = f"{'Решена' if attempt.is_successful else 'Попытка решения'} задача {attempt.task_id}"
            
            activities.append({
                'user_id': attempt.user_id,
                'activity_type': activity_type,
                'description': description,
                'task_id': attempt.task_id,
                'timestamp': attempt.created_at,
                'metadata': {
                    'language': attempt.language,
                    'execution_time_ms': attempt.execution_time_ms,
                    'is_successful': attempt.is_successful
                }
            })
        
        return activities 


