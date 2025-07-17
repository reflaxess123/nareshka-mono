"""Исключения для работы с заданиями"""

from app.shared.exceptions.base import BaseAppException, ResourceNotFoundException, ValidationException, CodeExecutionException


class TaskError(BaseAppException):
    """Базовое исключение для работы с заданиями"""
    
    def __init__(self, message: str = "Ошибка при работе с заданиями", details: dict = None):
        super().__init__(
            message=message,
            error_code="TASK_ERROR",
            status_code=500,
            details=details,
            user_message=message
        )


class TaskNotFoundError(ResourceNotFoundException):
    """Исключение при отсутствии задания"""
    
    def __init__(self, task_id: str):
        super().__init__(
            resource_type="Task",
            resource_id=task_id
        )


class TaskValidationError(ValidationException):
    """Исключение валидации данных задания"""
    
    def __init__(self, field: str, message: str = None):
        full_message = f"Ошибка валидации поля '{field}'" + (f": {message}" if message else "")
        super().__init__(
            message=full_message,
            field=field
        )


class TaskAttemptError(TaskError):
    """Исключение при ошибке работы с попытками решения"""
    
    def __init__(self, message: str = "Ошибка при работе с попытками решения"):
        super().__init__(message)


class TaskSolutionError(TaskError):
    """Исключение при ошибке работы с решениями задач"""
    
    def __init__(self, message: str = "Ошибка при работе с решениями задач"):
        super().__init__(message)


class TaskCodeExecutionError(CodeExecutionException):
    """Исключение при ошибке выполнения кода"""
    
    def __init__(self, message: str = "Ошибка выполнения кода", execution_details: str = None):
        super().__init__(
            message=message,
            details={"execution_details": execution_details} if execution_details else None
        )


class TaskInvalidLanguageError(TaskValidationError):
    """Исключение при неподдерживаемом языке программирования"""
    
    def __init__(self, language: str):
        super().__init__(
            field="language",
            message=f"Язык программирования '{language}' не поддерживается"
        ) 


