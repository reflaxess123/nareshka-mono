"""Репозиторий для работы с попытками решения и решениями задач"""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from app.features.task.exceptions.task_exceptions import (
    TaskAttemptError,
    TaskSolutionError,
)
from app.shared.models.task_models import TaskAttempt, TaskSolution

logger = logging.getLogger(__name__)


class TaskAttemptRepository:
    """Репозиторий для работы с попытками решения и решениями задач"""

    def __init__(self, session: Session):
        self.session = session

    def create_task_attempt(
        self,
        user_id: int,
        task_id: int,
        task_type: str,
        code: str,
        language: str,
    ) -> TaskAttempt:
        """Создать попытку решения задачи"""
        try:
            attempt = TaskAttempt(
                id=str(uuid4()),
                user_id=user_id,
                task_id=task_id,
                task_type=task_type,
                code=code,
                language=language,
                created_at=datetime.utcnow(),
            )

            self.session.add(attempt)
            self.session.commit()
            self.session.refresh(attempt)

            logger.info(
                "Created task attempt",
                user_id=user_id,
                task_id=task_id,
                attempt_id=attempt.id,
            )

            return attempt

        except Exception as e:
            self.session.rollback()
            logger.error(
                f"Failed to create task attempt: {str(e)}",
                user_id=user_id,
                task_id=task_id,
            )
            raise TaskAttemptError(f"Не удалось создать попытку решения: {str(e)}")

    def create_task_solution(
        self,
        user_id: int,
        task_id: int,
        task_type: str,
        code: str,
        language: str,
        is_correct: bool = False,
        execution_time: Optional[float] = None,
        memory_usage: Optional[int] = None,
        test_results: Optional[str] = None,
    ) -> TaskSolution:
        """Создать решение задачи"""
        try:
            solution = TaskSolution(
                id=str(uuid4()),
                user_id=user_id,
                task_id=task_id,
                task_type=task_type,
                code=code,
                language=language,
                is_correct=is_correct,
                execution_time=execution_time,
                memory_usage=memory_usage,
                test_results=test_results,
                created_at=datetime.utcnow(),
            )

            self.session.add(solution)
            self.session.commit()
            self.session.refresh(solution)

            logger.info(
                "Created task solution",
                user_id=user_id,
                task_id=task_id,
                solution_id=solution.id,
                is_correct=is_correct,
            )

            return solution

        except Exception as e:
            self.session.rollback()
            logger.error(
                f"Failed to create task solution: {str(e)}",
                user_id=user_id,
                task_id=task_id,
            )
            raise TaskSolutionError(f"Не удалось создать решение: {str(e)}")

    def get_user_task_attempts(
        self,
        user_id: int,
        task_id: Optional[int] = None,
        task_type: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[TaskAttempt]:
        """Получить попытки решения пользователя"""
        query = self.session.query(TaskAttempt).filter(TaskAttempt.user_id == user_id)

        if task_id is not None:
            query = query.filter(TaskAttempt.task_id == task_id)

        if task_type is not None:
            query = query.filter(TaskAttempt.task_type == task_type)

        query = query.order_by(TaskAttempt.created_at.desc())

        if limit is not None:
            query = query.limit(limit)

        return query.all()

    def get_user_task_solutions(
        self,
        user_id: int,
        task_id: Optional[int] = None,
        task_type: Optional[str] = None,
        only_correct: bool = False,
        limit: Optional[int] = None,
    ) -> List[TaskSolution]:
        """Получить решения пользователя"""
        query = self.session.query(TaskSolution).filter(TaskSolution.user_id == user_id)

        if task_id is not None:
            query = query.filter(TaskSolution.task_id == task_id)

        if task_type is not None:
            query = query.filter(TaskSolution.task_type == task_type)

        if only_correct:
            query = query.filter(TaskSolution.is_correct == True)

        query = query.order_by(TaskSolution.created_at.desc())

        if limit is not None:
            query = query.limit(limit)

        return query.all()

    def get_user_solution_stats(self, user_id: int) -> dict:
        """Получить статистику решений пользователя"""
        total_attempts = (
            self.session.query(TaskAttempt)
            .filter(TaskAttempt.user_id == user_id)
            .count()
        )

        total_solutions = (
            self.session.query(TaskSolution)
            .filter(TaskSolution.user_id == user_id)
            .count()
        )

        correct_solutions = (
            self.session.query(TaskSolution)
            .filter(TaskSolution.user_id == user_id)
            .filter(TaskSolution.is_correct == True)
            .count()
        )

        success_rate = (
            (correct_solutions / total_solutions * 100) if total_solutions > 0 else 0
        )

        return {
            "total_attempts": total_attempts,
            "total_solutions": total_solutions,
            "correct_solutions": correct_solutions,
            "success_rate": round(success_rate, 2),
        }

    def delete_task_attempt(self, attempt_id: str, user_id: int) -> bool:
        """Удалить попытку решения (только свою)"""
        attempt = (
            self.session.query(TaskAttempt)
            .filter(TaskAttempt.id == attempt_id)
            .filter(TaskAttempt.user_id == user_id)
            .first()
        )

        if not attempt:
            return False

        try:
            self.session.delete(attempt)
            self.session.commit()
            logger.info("Deleted task attempt", attempt_id=attempt_id, user_id=user_id)
            return True
        except Exception as e:
            self.session.rollback()
            logger.error(
                f"Failed to delete task attempt: {str(e)}",
                attempt_id=attempt_id,
                user_id=user_id,
            )
            return False

    def delete_task_solution(self, solution_id: str, user_id: int) -> bool:
        """Удалить решение (только свое)"""
        solution = (
            self.session.query(TaskSolution)
            .filter(TaskSolution.id == solution_id)
            .filter(TaskSolution.user_id == user_id)
            .first()
        )

        if not solution:
            return False

        try:
            self.session.delete(solution)
            self.session.commit()
            logger.info(
                "Deleted task solution", solution_id=solution_id, user_id=user_id
            )
            return True
        except Exception as e:
            self.session.rollback()
            logger.error(
                f"Failed to delete task solution: {str(e)}",
                solution_id=solution_id,
                user_id=user_id,
            )
            return False
