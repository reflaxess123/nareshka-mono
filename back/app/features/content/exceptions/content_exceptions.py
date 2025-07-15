"""
Content Feature Exceptions

Специфичные исключения для работы с контентом.
"""

from app.shared.exceptions.base import (
    BaseAppException,
    ResourceNotFoundException,
    ValidationException,
    BusinessLogicException,
)


class ContentError(BaseAppException):
    """Базовое исключение для content feature"""
    
    def __init__(self, message: str = "Content operation failed"):
        super().__init__(message, error_code="CONTENT_ERROR")


class ContentNotFoundError(ResourceNotFoundException):
    """Исключение когда контент не найден"""
    
    def __init__(self, content_id: str | None = None, content_type: str = "content"):
        if content_id:
            super().__init__(content_type, content_id)
        else:
            super().__init__(content_type)


class ContentBlockNotFoundError(ContentNotFoundError):
    """Блок контента не найден"""
    
    def __init__(self, block_id: str):
        super().__init__(block_id, "content block")


class ContentFileNotFoundError(ContentNotFoundError):
    """Файл контента не найден"""
    
    def __init__(self, file_id: str):
        super().__init__(file_id, "content file")


class ContentFileError(ContentError):
    """Ошибка при работе с файлом контента"""
    
    def __init__(self, message: str = "Content file operation failed"):
        super().__init__(message)
        self.error_code = "CONTENT_FILE_ERROR"


class ContentValidationError(ValidationException):
    """Ошибка валидации данных контента"""
    
    def __init__(self, message: str = "Content validation failed", field: str | None = None):
        super().__init__(message, field=field)


class ContentProgressError(BusinessLogicException):
    """Ошибка при работе с прогрессом контента"""
    
    def __init__(self, message: str = "Content progress operation failed"):
        super().__init__(message, business_rule="content_progress")


class InvalidProgressActionError(ContentProgressError):
    """Некорректное действие с прогрессом"""
    
    def __init__(self, action: str):
        message = f"Invalid progress action: '{action}'. Must be 'increment' or 'decrement'"
        super().__init__(message)


class ContentCategoryError(ContentError):
    """Ошибка при работе с категориями контента"""
    
    def __init__(self, message: str = "Content category operation failed"):
        super().__init__(message)
        self.error_code = "CONTENT_CATEGORY_ERROR"


class WebDAVPathError(ContentFileError):
    """Ошибка с путем WebDAV"""
    
    def __init__(self, path: str, message: str | None = None):
        if message is None:
            message = f"Invalid WebDAV path: '{path}'"
        super().__init__(message)
        self.error_code = "WEBDAV_PATH_ERROR"
        self.path = path 


