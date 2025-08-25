"""
Dependency Injection Container для приложения
"""

from typing import Any, Callable, Dict, Type, TypeVar

from app.core.logging import get_logger
from app.shared.database import get_session

logger = get_logger(__name__)

T = TypeVar("T")


class DIContainer:
    """
    Простой DI Container для управления зависимостями
    """

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        self._configurations: Dict[str, Any] = {}

    def register_singleton(
        self, service_type: Type[T], factory: Callable[[], T]
    ) -> None:
        """Регистрация синглтона"""
        key = self._get_key(service_type)
        self._factories[key] = factory
        logger.debug(f"Registered singleton: {key}")

    def register_transient(
        self, service_type: Type[T], factory: Callable[[], T]
    ) -> None:
        """Регистрация транзиентного сервиса"""
        key = self._get_key(service_type)
        self._services[key] = factory
        logger.debug(f"Registered transient: {key}")

    def register_instance(self, service_type: Type[T], instance: T) -> None:
        """Регистрация готового экземпляра"""
        key = self._get_key(service_type)
        self._singletons[key] = instance
        logger.debug(f"Registered instance: {key}")

    def register_config(self, key: str, value: Any) -> None:
        """Регистрация конфигурации"""
        self._configurations[key] = value
        logger.debug(f"Registered config: {key}")

    def get(self, service_type: Type[T]) -> T:
        """Получить сервис"""
        key = self._get_key(service_type)

        # Проверяем синглтоны
        if key in self._singletons:
            return self._singletons[key]

        # Проверяем фабрики синглтонов
        if key in self._factories:
            instance = self._factories[key]()
            self._singletons[key] = instance
            logger.debug(f"Created singleton: {key}")
            return instance

        # Проверяем транзиентные сервисы
        if key in self._services:
            instance = self._services[key]()
            logger.debug(f"Created transient: {key}")
            return instance

        raise ValueError(f"Service {key} not registered")

    def get_config(self, key: str, default: Any = None) -> Any:
        """Получить конфигурацию"""
        return self._configurations.get(key, default)

    def _get_key(self, service_type: Type) -> str:
        """Получить ключ для типа сервиса"""
        return f"{service_type.__module__}.{service_type.__name__}"

    def reset(self) -> None:
        """Сбросить контейнер"""
        self._singletons.clear()
        logger.debug("DI Container reset")


# Глобальный контейнер
_container = DIContainer()


def get_container() -> DIContainer:
    """Получить глобальный контейнер"""
    return _container


def configure_container():
    """Настроить контейнер с зависимостями"""
    container = get_container()

    # Регистрируем репозитории
    from app.features.auth.repositories.sqlalchemy_user_repository import (
        SQLAlchemyUserRepository,
    )
    from app.features.code_editor.repositories.code_editor_repository import (
        CodeEditorRepository,
    )
    from app.features.content.repositories.content_repository import ContentRepository
    from app.features.mindmap.repositories.mindmap_repository import MindMapRepository
    from app.features.progress.repositories.progress_repository import (
        ProgressRepository,
    )
    from app.features.stats.repositories.stats_repository import StatsRepository
    from app.features.task.repositories.task_repository import TaskRepository
    from app.features.theory.repositories.theory_repository import TheoryRepository

    # Репозитории с сессиями БД
    db_repositories = [
        ContentRepository,
        TaskRepository, 
        TheoryRepository,
        ProgressRepository,
        StatsRepository,
        MindMapRepository
    ]
    
    for repo_class in db_repositories:
        container.register_transient(
            repo_class, lambda cls=repo_class: cls(get_session())
        )
    
    # Специальные репозитории без сессий
    container.register_transient(
        SQLAlchemyUserRepository, lambda: SQLAlchemyUserRepository()
    )
    container.register_transient(CodeEditorRepository, lambda: CodeEditorRepository())

    # Регистрируем сервисы
    from app.features.auth.services.auth_service import AuthService
    from app.features.code_editor.services.ai_test_generator_service import (
        AITestGeneratorService,
    )
    from app.features.code_editor.services.code_editor_service import CodeEditorService
    from app.features.code_editor.services.enhanced_code_executor_service import (
        EnhancedCodeExecutorService,
    )
    from app.features.content.services.content_service import ContentService
    from app.features.mindmap.services.mindmap_service import MindMapService
    from app.features.progress.services.progress_service import ProgressService
    from app.features.stats.services.stats_service import StatsService
    from app.features.task.services.task_service import TaskService
    from app.features.theory.services.theory_service import TheoryService

    # Сервисы с простыми зависимостями (один репозиторий)
    simple_services = [
        (AuthService, SQLAlchemyUserRepository),
        (ContentService, ContentRepository),
        (TaskService, TaskRepository),
        (TheoryService, TheoryRepository),
        (ProgressService, ProgressRepository),
        (StatsService, StatsRepository),
        (CodeEditorService, CodeEditorRepository),
        (EnhancedCodeExecutorService, CodeEditorRepository),
        (MindMapService, MindMapRepository),
    ]
    
    for service_class, repo_class in simple_services:
        container.register_transient(
            service_class, lambda svc=service_class, repo=repo_class: svc(container.get(repo))
        )
    
    # Сервисы со сложными зависимостями
    container.register_transient(
        AITestGeneratorService, 
        lambda: AITestGeneratorService(
            container.get(ContentRepository), 
            container.get(TaskRepository)
        )
    )

    logger.info("DI Container configured successfully")




# FastAPI Dependencies
def create_service_dependency(service_type: Type[T]) -> Callable[[], T]:
    """Создать FastAPI dependency для сервиса"""

    def get_service() -> T:
        container = get_container()
        return container.get(service_type)

    return get_service




# Middleware для настройки контейнера при старте приложения
def setup_di_container():
    """Настроить DI контейнер при старте приложения"""
    configure_container()
    logger.info("DI Container setup completed")


# Utility для тестирования
def create_test_container() -> DIContainer:
    """Создать контейнер для тестирования"""
    container = DIContainer()

    # Регистрируем моки для тестирования
    from unittest.mock import Mock

    container.register_instance(SQLAlchemyUserRepository, Mock())
    container.register_instance(ContentRepository, Mock())
    container.register_instance(TaskRepository, Mock())

    return container
