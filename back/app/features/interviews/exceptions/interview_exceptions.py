"""Исключения для interview feature"""

from app.shared.exceptions.base import BaseAppException


class InterviewNotFoundError(BaseAppException):
    """Интервью не найдено"""

    pass


class CompanyNotFoundError(BaseAppException):
    """Компания не найдена"""

    pass


class InvalidFilterError(BaseAppException):
    """Неверные параметры фильтрации"""

    pass


# Исключения для категорий
class CategoryNotFoundError(BaseAppException):
    """Категория не найдена"""

    def __init__(self, category_id: str):
        super().__init__(f"Category with id '{category_id}' not found")
        self.category_id = category_id


class ClusterNotFoundError(BaseAppException):
    """Кластер не найден"""

    def __init__(self, cluster_id: int):
        super().__init__(f"Cluster with id {cluster_id} not found")
        self.cluster_id = cluster_id


class QuestionNotFoundError(BaseAppException):
    """Вопрос не найден"""

    def __init__(self, question_id: str):
        super().__init__(f"Question with id '{question_id}' not found")
        self.question_id = question_id
