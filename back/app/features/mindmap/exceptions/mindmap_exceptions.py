"""Исключения для работы с ментальными картами"""

from app.shared.exceptions.base import BaseAppException, ResourceNotFoundException


class MindMapError(BaseAppException):
    """Базовое исключение для работы с mindmap"""

    def __init__(
        self,
        message: str = "Ошибка при работе с ментальной картой",
        details: dict = None,
    ):
        super().__init__(
            message=message,
            error_code="MINDMAP_ERROR",
            status_code=500,
            details=details,
            user_message=message,
        )


class TechnologyNotSupportedError(MindMapError):
    """Исключение при неподдерживаемой технологии"""

    def __init__(self, technology: str):
        super().__init__(
            message=f"Технология '{technology}' не поддерживается",
            details={"technology": technology},
        )


class TopicNotFoundError(ResourceNotFoundException):
    """Исключение при отсутствии топика"""

    def __init__(self, topic_key: str, technology: str = None):
        tech_info = f" для технологии '{technology}'" if technology else ""
        message = f"Топик '{topic_key}'{tech_info}"
        details = {"topic_key": topic_key}
        if technology:
            details["technology"] = technology

        super().__init__(
            resource_type="Topic",
            resource_id=topic_key,
            message=message,
            details=details,
        )


class TaskNotFoundError(ResourceNotFoundException):
    """Исключение при отсутствии задачи"""

    def __init__(self, task_id: str):
        super().__init__(
            resource_type="Task",
            resource_id=task_id,
            message=f"Задача с ID '{task_id}'",
        )
