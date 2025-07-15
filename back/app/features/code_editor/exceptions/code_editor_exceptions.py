"""Исключения для работы с редактором кода"""

from app.core.exceptions import BaseApplicationException, NotFoundException


class CodeEditorError(BaseApplicationException):
    """Базовое исключение для работы с редактором кода"""
    
    def __init__(self, message: str = "Ошибка при работе с редактором кода", details: str = None):
        from app.core.exceptions import ErrorCode
        super().__init__(message, ErrorCode.INTERNAL_ERROR, details, 500)


class UnsupportedLanguageError(CodeEditorError):
    """Исключение при неподдерживаемом языке программирования"""
    
    def __init__(self, language: str):
        super().__init__(f"Язык программирования '{language}' не поддерживается")


class CodeExecutionError(CodeEditorError):
    """Исключение при ошибке выполнения кода"""
    
    def __init__(self, execution_id: str, message: str = None):
        error_message = f"Ошибка выполнения кода {execution_id}"
        if message:
            error_message += f": {message}"
        super().__init__(error_message)


class UnsafeCodeError(CodeEditorError):
    """Исключение при обнаружении небезопасного кода"""
    
    def __init__(self, reason: str = "Код содержит потенциально опасные конструкции"):
        super().__init__(f"Небезопасный код: {reason}")


class SolutionNotFoundError(NotFoundException):
    """Исключение при отсутствии решения"""
    
    def __init__(self, solution_id: str = None, user_id: int = None, block_id: str = None):
        if solution_id:
            super().__init__(f"Решение с ID '{solution_id}'")
        elif user_id and block_id:
            super().__init__(f"Решение пользователя {user_id} для блока '{block_id}'")
        else:
            super().__init__("Решение")


class TestCaseExecutionError(CodeEditorError):
    """Исключение при ошибке выполнения тест-кейса"""
    
    def __init__(self, test_case_id: str, message: str = None):
        error_message = f"Ошибка выполнения тест-кейса {test_case_id}"
        if message:
            error_message += f": {message}"
        super().__init__(error_message) 


