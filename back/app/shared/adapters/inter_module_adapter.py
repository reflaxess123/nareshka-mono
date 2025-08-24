"""
Адаптерные слои для межмодульной коммуникации
"""

from typing import Any, Dict, List, Optional, Protocol

from app.core.logging import get_logger

logger = get_logger(__name__)


# ===== PROTOCOLS FOR INTER-MODULE COMMUNICATION =====


class TaskProviderProtocol(Protocol):
    """Протокол для доступа к задачам"""

    def get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Получить задачу по ID"""
        ...

    def get_tasks_by_ids(self, task_ids: List[str]) -> List[Dict[str, Any]]:
        """Получить задачи по списку ID"""
        ...


class ContentProviderProtocol(Protocol):
    """Протокол для доступа к контенту"""

    def get_content_by_id(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Получить контент по ID"""
        ...

    def get_content_by_ids(self, content_ids: List[str]) -> List[Dict[str, Any]]:
        """Получить контент по списку ID"""
        ...


class UserProviderProtocol(Protocol):
    """Протокол для доступа к пользователям"""

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить пользователя по ID"""
        ...

    def get_users_by_ids(self, user_ids: List[int]) -> List[Dict[str, Any]]:
        """Получить пользователей по списку ID"""
        ...


# ===== SHARED DATA TRANSFER OBJECTS =====


class TaskInfo:
    """Информация о задаче для межмодульного обмена"""

    def __init__(
        self, task_id: str, title: str, description: str, task_type: str, **kwargs
    ):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.task_type = task_type
        self.additional_data = kwargs

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "task_type": self.task_type,
            **self.additional_data,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskInfo":
        return cls(**data)


class ContentInfo:
    """Информация о контенте для межмодульного обмена"""

    def __init__(self, content_id: str, title: str, content_type: str, **kwargs):
        self.content_id = content_id
        self.title = title
        self.content_type = content_type
        self.additional_data = kwargs

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content_id": self.content_id,
            "title": self.title,
            "content_type": self.content_type,
            **self.additional_data,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContentInfo":
        return cls(**data)


class UserInfo:
    """Информация о пользователе для межмодульного обмена"""

    def __init__(self, user_id: int, username: str, email: str, **kwargs):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.additional_data = kwargs

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            **self.additional_data,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserInfo":
        return cls(**data)


# ===== ADAPTER IMPLEMENTATIONS =====


class TaskAdapter:
    """Адаптер для работы с задачами"""

    def __init__(self, task_provider: TaskProviderProtocol):
        self.task_provider = task_provider

    def get_task_info(self, task_id: str) -> Optional[TaskInfo]:
        """Получить информацию о задаче"""
        try:
            task_data = self.task_provider.get_task_by_id(task_id)
            if task_data:
                return TaskInfo.from_dict(task_data)
            return None
        except Exception as e:
            logger.error(f"Error getting task info: {e}", extra={"task_id": task_id})
            return None

    def get_tasks_info(self, task_ids: List[str]) -> List[TaskInfo]:
        """Получить информацию о задачах"""
        try:
            tasks_data = self.task_provider.get_tasks_by_ids(task_ids)
            return [TaskInfo.from_dict(task_data) for task_data in tasks_data]
        except Exception as e:
            logger.error(f"Error getting tasks info: {e}", extra={"task_ids": task_ids})
            return []


class ContentAdapter:
    """Адаптер для работы с контентом"""

    def __init__(self, content_provider: ContentProviderProtocol):
        self.content_provider = content_provider

    def get_content_info(self, content_id: str) -> Optional[ContentInfo]:
        """Получить информацию о контенте"""
        try:
            content_data = self.content_provider.get_content_by_id(content_id)
            if content_data:
                return ContentInfo.from_dict(content_data)
            return None
        except Exception as e:
            logger.error(
                f"Error getting content info: {e}", extra={"content_id": content_id}
            )
            return None

    def get_contents_info(self, content_ids: List[str]) -> List[ContentInfo]:
        """Получить информацию о контенте"""
        try:
            contents_data = self.content_provider.get_content_by_ids(content_ids)
            return [
                ContentInfo.from_dict(content_data) for content_data in contents_data
            ]
        except Exception as e:
            logger.error(
                f"Error getting contents info: {e}", extra={"content_ids": content_ids}
            )
            return []


class UserAdapter:
    """Адаптер для работы с пользователями"""

    def __init__(self, user_provider: UserProviderProtocol):
        self.user_provider = user_provider

    def get_user_info(self, user_id: int) -> Optional[UserInfo]:
        """Получить информацию о пользователе"""
        try:
            user_data = self.user_provider.get_user_by_id(user_id)
            if user_data:
                return UserInfo.from_dict(user_data)
            return None
        except Exception as e:
            logger.error(f"Error getting user info: {e}", extra={"user_id": user_id})
            return None

    def get_users_info(self, user_ids: List[int]) -> List[UserInfo]:
        """Получить информацию о пользователях"""
        try:
            users_data = self.user_provider.get_users_by_ids(user_ids)
            return [UserInfo.from_dict(user_data) for user_data in users_data]
        except Exception as e:
            logger.error(f"Error getting users info: {e}", extra={"user_ids": user_ids})
            return []


# ===== INTER-MODULE FACADE =====


class InterModuleFacade:
    """Фасад для межмодульной коммуникации"""

    def __init__(self):
        self._task_adapter: Optional[TaskAdapter] = None
        self._content_adapter: Optional[ContentAdapter] = None
        self._user_adapter: Optional[UserAdapter] = None

    def register_task_provider(self, provider: TaskProviderProtocol):
        """Зарегистрировать провайдер задач"""
        self._task_adapter = TaskAdapter(provider)
        logger.info("Task provider registered")

    def register_content_provider(self, provider: ContentProviderProtocol):
        """Зарегистрировать провайдер контента"""
        self._content_adapter = ContentAdapter(provider)
        logger.info("Content provider registered")

    def register_user_provider(self, provider: UserProviderProtocol):
        """Зарегистрировать провайдер пользователей"""
        self._user_adapter = UserAdapter(provider)
        logger.info("User provider registered")

    @property
    def tasks(self) -> TaskAdapter:
        """Получить адаптер задач"""
        if not self._task_adapter:
            raise ValueError("Task provider not registered")
        return self._task_adapter

    @property
    def content(self) -> ContentAdapter:
        """Получить адаптер контента"""
        if not self._content_adapter:
            raise ValueError("Content provider not registered")
        return self._content_adapter

    @property
    def users(self) -> UserAdapter:
        """Получить адаптер пользователей"""
        if not self._user_adapter:
            raise ValueError("User provider not registered")
        return self._user_adapter


# ===== GLOBAL FACADE INSTANCE =====

_inter_module_facade = InterModuleFacade()


def get_inter_module_facade() -> InterModuleFacade:
    """Получить глобальный фасад для межмодульной коммуникации"""
    return _inter_module_facade


# ===== PROVIDER IMPLEMENTATIONS =====


class TaskRepositoryProvider:
    """Провайдер для TaskRepository"""

    def __init__(self, task_repository):
        self.task_repository = task_repository

    def get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Получить задачу по ID"""
        try:
            # Здесь должна быть реализация получения задачи
            # Это пример, нужно адаптировать под реальный TaskRepository
            task = self.task_repository.get_by_id(task_id)
            if task:
                return {
                    "task_id": str(task.id),
                    "title": getattr(task, "title", "Unknown"),
                    "description": getattr(task, "description", ""),
                    "task_type": getattr(task, "item_type", "unknown"),
                }
            return None
        except Exception as e:
            logger.error(f"Error getting task by id: {e}")
            return None

    def get_tasks_by_ids(self, task_ids: List[str]) -> List[Dict[str, Any]]:
        """Получить задачи по списку ID"""
        try:
            result = []
            for task_id in task_ids:
                task = self.get_task_by_id(task_id)
                if task:
                    result.append(task)
            return result
        except Exception as e:
            logger.error(f"Error getting tasks by ids: {e}")
            return []


class ContentRepositoryProvider:
    """Провайдер для ContentRepository"""

    def __init__(self, content_repository):
        self.content_repository = content_repository

    def get_content_by_id(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Получить контент по ID"""
        try:
            # Здесь должна быть реализация получения контента
            # Это пример, нужно адаптировать под реальный ContentRepository
            content = self.content_repository.get_by_id(content_id)
            if content:
                return {
                    "content_id": str(content.id),
                    "title": getattr(content, "title", "Unknown"),
                    "content_type": getattr(content, "blockType", "unknown"),
                }
            return None
        except Exception as e:
            logger.error(f"Error getting content by id: {e}")
            return None

    def get_content_by_ids(self, content_ids: List[str]) -> List[Dict[str, Any]]:
        """Получить контент по списку ID"""
        try:
            result = []
            for content_id in content_ids:
                content = self.get_content_by_id(content_id)
                if content:
                    result.append(content)
            return result
        except Exception as e:
            logger.error(f"Error getting content by ids: {e}")
            return []


def setup_inter_module_adapters():
    """Настроить адаптеры для межмодульной коммуникации"""
    facade = get_inter_module_facade()

    # Здесь можно зарегистрировать провайдеры
    # facade.register_task_provider(TaskRepositoryProvider(task_repository))
    # facade.register_content_provider(ContentRepositoryProvider(content_repository))

    logger.info("Inter-module adapters setup completed")
