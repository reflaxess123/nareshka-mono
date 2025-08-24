"""
Categories Exceptions - исключения для работы с категориями
"""

from app.shared.exceptions.base import BaseAppException


class CategoryError(BaseAppException):
    """Базовое исключение для операций с категориями"""

    pass


class CategoryNotFoundError(CategoryError):
    """Категория не найдена"""

    def __init__(self, category_id: str):
        super().__init__(f"Category with id '{category_id}' not found")
        self.category_id = category_id


class ClusterNotFoundError(CategoryError):
    """Кластер не найден"""

    def __init__(self, cluster_id: int):
        super().__init__(f"Cluster with id {cluster_id} not found")
        self.cluster_id = cluster_id


class QuestionNotFoundError(CategoryError):
    """Вопрос не найден"""

    def __init__(self, question_id: str):
        super().__init__(f"Question with id '{question_id}' not found")
        self.question_id = question_id


class InvalidSearchQueryError(CategoryError):
    """Некорректный поисковый запрос"""

    def __init__(self, query: str, reason: str = "Invalid search query"):
        super().__init__(f"{reason}: '{query}'")
        self.query = query
        self.reason = reason
