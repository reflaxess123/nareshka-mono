"""Исключения для interview feature"""

from app.shared.exceptions.base import BaseException


class InterviewNotFoundError(BaseException):
    """Интервью не найдено"""
    pass


class CompanyNotFoundError(BaseException):
    """Компания не найдена"""
    pass


class InvalidFilterError(BaseException):
    """Неверные параметры фильтрации"""
    pass