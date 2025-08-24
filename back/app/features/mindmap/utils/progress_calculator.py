"""Утилиты для подсчета прогресса"""

from typing import Dict, Any
from app.features.mindmap.utils.enums import ProgressStatus


class ProgressCalculator:
    """Калькулятор прогресса выполнения задач"""

    @staticmethod
    def calculate_completion_rate(completed_tasks: int, total_tasks: int) -> float:
        """Вычислить процент выполнения"""
        if total_tasks <= 0:
            return 0.0
        return round((completed_tasks / total_tasks * 100), 1)

    @staticmethod
    def get_progress_status(completion_rate: float) -> ProgressStatus:
        """Определить статус прогресса по проценту"""
        if completion_rate == 100.0:
            return ProgressStatus.COMPLETED
        elif completion_rate > 0:
            return ProgressStatus.IN_PROGRESS
        else:
            return ProgressStatus.NOT_STARTED

    @staticmethod
    def build_progress_dict(
        total_tasks: int,
        completed_tasks: int
    ) -> Dict[str, Any]:
        """Построить словарь с информацией о прогрессе"""
        completion_rate = ProgressCalculator.calculate_completion_rate(
            completed_tasks, total_tasks
        )
        status = ProgressCalculator.get_progress_status(completion_rate)

        return {
            "totalTasks": total_tasks,
            "completedTasks": completed_tasks,
            "completionRate": completion_rate,
            "status": status.value,
        }

    @staticmethod
    def build_task_progress_dict(solved_count: int) -> Dict[str, Any]:
        """Построить словарь прогресса для одной задачи"""
        return {
            "solvedCount": solved_count,
            "isCompleted": solved_count > 0,
        }
