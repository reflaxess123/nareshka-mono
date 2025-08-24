"""Константы для progress модуля"""

# Время
TIME_MS_TO_MINUTES = 1000 * 60

# Лимиты по умолчанию
DEFAULT_LIMIT = 50
MAX_LIMIT = 100
DEFAULT_PAGE = 1

# Периоды аналитики
ANALYTICS_PERIODS = {
    "day": 1,
    "week": 7, 
    "month": 30
}

# Статусы прогресса
PROGRESS_STATUS_NOT_STARTED = "not_started"
PROGRESS_STATUS_IN_PROGRESS = "in_progress"
PROGRESS_STATUS_COMPLETED = "completed"

# Типы активности
ACTIVITY_TYPE_TASK_ATTEMPTED = "task_attempted"
ACTIVITY_TYPE_TASK_SOLVED = "task_solved"