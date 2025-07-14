"""Исключения для работы с теоретическими карточками"""

from app.core.exceptions import BaseApplicationException, NotFoundException


class TheoryError(BaseApplicationException):
    """Базовое исключение для работы с теорией"""
    
    def __init__(self, message: str = "Ошибка при работе с теорией", details: str = None):
        from app.core.exceptions import ErrorCode
        super().__init__(message, ErrorCode.INTERNAL_ERROR, details, 500)


class TheoryCardNotFoundError(NotFoundException):
    """Исключение при отсутствии теоретической карточки"""
    
    def __init__(self, card_id: str):
        super().__init__("TheoryCard", card_id)


class TheoryProgressError(TheoryError):
    """Исключение при ошибке работы с прогрессом"""
    
    def __init__(self, message: str = "Ошибка при работе с прогрессом изучения"):
        super().__init__(message)


class InvalidProgressActionError(TheoryError):
    """Исключение при недопустимом действии с прогрессом"""
    
    def __init__(self, action: str):
        super().__init__(f"Недопустимое действие: {action}. Разрешены: increment, decrement")


class InvalidReviewRatingError(TheoryError):
    """Исключение при недопустимой оценке повторения"""
    
    def __init__(self, rating: str):
        super().__init__(f"Недопустимая оценка: {rating}. Разрешены: again, hard, good, easy")


class TheoryValidationError(TheoryError):
    """Исключение валидации данных теории"""
    
    def __init__(self, field: str, value: str, message: str = None):
        error_message = f"Ошибка валидации поля '{field}' со значением '{value}'"
        if message:
            error_message += f": {message}"
        super().__init__(error_message) 


