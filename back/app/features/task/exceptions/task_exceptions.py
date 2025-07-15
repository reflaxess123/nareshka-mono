"""Исключения для работы с заданиями"""

from app.core.exceptions import BaseApplicationException, NotFoundException, ValidationException


class TaskError(BaseApplicationException):
    """Базовое исключение для работы с заданиями"""
    
    def __init__(self, message: str = "Ошибка при работе с заданиями", details: str = None):
        from app.core.exceptions import ErrorCode
        super().__init__(message, ErrorCode.INTERNAL_ERROR, details, 500)


class TaskNotFoundError(NotFoundException):
    """Исключение при отсутствии задания"""
    
    def __init__(self, task_id: str):
        super().__init__("Task", task_id)


class TaskValidationError(ValidationException):
    """Исключение валидации данных задания"""
    
    def __init__(self, field: str, message: str = None):
        super().__init__(f"Ошибка валидации поля '{field}'" + (f": {message}" if message else ""), field)


class TaskAttemptError(TaskError):
    """Исключение при ошибке работы с попытками решения"""
    
    def __init__(self, message: str = "Ошибка при работе с попытками решения"):
        super().__init__(message)


class TaskSolutionError(TaskError):
    """Исключение при ошибке работы с решениями задач"""
    
    def __init__(self, message: str = "Ошибка при работе с решениями задач"):
        super().__init__(message)


class TaskCodeExecutionError(TaskError):
    """Исключение при ошибке выполнения кода"""
    
    def __init__(self, message: str = "Ошибка выполнения кода", execution_details: str = None):
        super().__init__(message, execution_details)


class TaskInvalidLanguageError(TaskValidationError):
    """Исключение при неподдерживаемом языке программирования"""
    
    def __init__(self, language: str):
        super().__init__("language", f"Язык программирования '{language}' не поддерживается") 


