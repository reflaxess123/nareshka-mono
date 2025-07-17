"""Исключения для работы с редактором кода"""

from app.shared.exceptions.base import BaseAppException, ResourceNotFoundException, ValidationException, CodeExecutionException


class CodeEditorError(BaseAppException):
    """Базовое исключение для работы с редактором кода"""
    
    def __init__(self, message: str = "Ошибка при работе с редактором кода", details: dict = None):
        super().__init__(
            message=message,
            error_code="CODE_EDITOR_ERROR",
            status_code=500,
            details=details,
            user_message=message
        )


class UnsupportedLanguageError(ValidationException):
    """Исключение при неподдерживаемом языке программирования"""
    
    def __init__(self, language: str):
        super().__init__(
            message=f"Язык программирования '{language}' не поддерживается",
            field="language",
            value=language
        )


class CodeExecutionError(CodeExecutionException):
    """Исключение при ошибке выполнения кода"""
    
    def __init__(self, execution_id: str, message: str = None):
        error_message = f"Ошибка выполнения кода {execution_id}"
        if message:
            error_message += f": {message}"
        super().__init__(
            message=error_message,
            details={"execution_id": execution_id, "error_details": message}
        )


class UnsafeCodeError(ValidationException):
    """Исключение при обнаружении небезопасного кода"""
    
    def __init__(self, reason: str = "Код содержит потенциально опасные конструкции"):
        super().__init__(
            message=f"Небезопасный код: {reason}",
            field="code",
            details={"security_reason": reason}
        )


class SolutionNotFoundError(ResourceNotFoundException):
    """Исключение при отсутствии решения"""
    
    def __init__(self, solution_id: str = None, user_id: int = None, block_id: str = None):
        if solution_id:
            super().__init__(
                resource_type="Solution",
                resource_id=solution_id,
                message=f"Решение с ID '{solution_id}'"
            )
        elif user_id and block_id:
            super().__init__(
                resource_type="Solution",
                resource_id=f"user-{user_id}-block-{block_id}",
                message=f"Решение пользователя {user_id} для блока '{block_id}'",
                details={"user_id": user_id, "block_id": block_id}
            )
        else:
            super().__init__(
                resource_type="Solution",
                message="Решение"
            )


class TestCaseExecutionError(CodeExecutionException):
    """Исключение при ошибке выполнения тест-кейса"""
    
    def __init__(self, test_case_id: str, message: str = None):
        error_message = f"Ошибка выполнения тест-кейса {test_case_id}"
        if message:
            error_message += f": {message}"
        super().__init__(
            message=error_message,
            details={"test_case_id": test_case_id, "error_details": message}
        ) 


