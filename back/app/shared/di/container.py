"""
Dependency Injection Container для приложения
"""

from typing import Dict, Any, TypeVar, Type, Callable, Optional
from functools import lru_cache
from sqlalchemy.orm import Session
from app.core.logging import get_logger
from app.shared.database import get_session

logger = get_logger(__name__)

T = TypeVar('T')


class DIContainer:
    """
    Простой DI Container для управления зависимостями
    """
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        self._configurations: Dict[str, Any] = {}
    
    def register_singleton(self, service_type: Type[T], factory: Callable[[], T]) -> None:
        """Регистрация синглтона"""
        key = self._get_key(service_type)
        self._factories[key] = factory
        logger.debug(f"Registered singleton: {key}")
    
    def register_transient(self, service_type: Type[T], factory: Callable[[], T]) -> None:
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
    from app.features.auth.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
    from app.features.content.repositories.content_repository import ContentRepository
    from app.features.task.repositories.task_repository import TaskRepository
    from app.features.theory.repositories.theory_repository import TheoryRepository
    from app.features.progress.repositories.progress_repository import ProgressRepository
    from app.features.stats.repositories.stats_repository import StatsRepository
    from app.features.code_editor.repositories.code_editor_repository import CodeEditorRepository
    from app.features.mindmap.repositories.mindmap_repository import MindMapRepository
    
    # Регистрируем как транзиентные (новый экземпляр каждый раз)
    container.register_transient(SQLAlchemyUserRepository, lambda: SQLAlchemyUserRepository())
    container.register_transient(ContentRepository, lambda: ContentRepository(get_session()))
    container.register_transient(TaskRepository, lambda: TaskRepository(get_session()))
    container.register_transient(TheoryRepository, lambda: TheoryRepository(get_session()))
    container.register_transient(ProgressRepository, lambda: ProgressRepository(get_session()))
    container.register_transient(StatsRepository, lambda: StatsRepository(get_session()))
    container.register_transient(CodeEditorRepository, lambda: CodeEditorRepository())
    container.register_transient(MindMapRepository, lambda: MindMapRepository(get_session()))
    
    # Регистрируем сервисы
    from app.features.auth.services.auth_service import AuthService
    from app.features.content.services.content_service import ContentService
    from app.features.task.services.task_service import TaskService
    from app.features.theory.services.theory_service import TheoryService
    from app.features.progress.services.progress_service import ProgressService
    from app.features.stats.services.stats_service import StatsService
    from app.features.code_editor.services.code_editor_service import CodeEditorService
    from app.features.code_editor.services.enhanced_code_executor_service import EnhancedCodeExecutorService
    from app.features.code_editor.services.ai_test_generator_service import AITestGeneratorService
    from app.features.mindmap.services.mindmap_service import MindMapService
    
    # Регистрируем как транзиентные с правильными зависимостями
    def create_auth_service():
        return AuthService(container.get(SQLAlchemyUserRepository))
    
    def create_content_service():
        return ContentService(container.get(ContentRepository))
    
    def create_task_service():
        return TaskService(container.get(TaskRepository))
    
    def create_theory_service():
        return TheoryService(container.get(TheoryRepository))
    
    def create_progress_service():
        return ProgressService(container.get(ProgressRepository))
    
    def create_stats_service():
        return StatsService(container.get(StatsRepository))
    
    def create_code_editor_service():
        return CodeEditorService(container.get(CodeEditorRepository))
    
    def create_code_executor_service():
        return EnhancedCodeExecutorService(container.get(CodeEditorRepository))
    
    def create_mindmap_service():
        return MindMapService(container.get(MindMapRepository))
    
    def create_ai_test_generator_service():
        return AITestGeneratorService(
            container.get(ContentRepository),
            container.get(TaskRepository)
        )
    
    container.register_transient(AuthService, create_auth_service)
    container.register_transient(ContentService, create_content_service)
    container.register_transient(TaskService, create_task_service)
    container.register_transient(TheoryService, create_theory_service)
    container.register_transient(ProgressService, create_progress_service)
    container.register_transient(StatsService, create_stats_service)
    container.register_transient(CodeEditorService, create_code_editor_service)
    container.register_transient(EnhancedCodeExecutorService, create_code_executor_service)
    container.register_transient(MindMapService, create_mindmap_service)
    container.register_transient(AITestGeneratorService, create_ai_test_generator_service)
    
    logger.info("DI Container configured successfully")


# Декоратор для внедрения зависимостей
def inject(service_type: Type[T]):
    """
    Декоратор для внедрения зависимостей
    
    Usage:
        @inject(AuthService)
        def my_function(auth_service: AuthService):
            # auth_service будет автоматически внедрен
            pass
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            container = get_container()
            service = container.get(service_type)
            return func(*args, service, **kwargs)
        return wrapper
    return decorator


# FastAPI Dependencies
def create_service_dependency(service_type: Type[T]) -> Callable[[], T]:
    """Создать FastAPI dependency для сервиса"""
    def get_service() -> T:
        container = get_container()
        return container.get(service_type)
    
    return get_service


class ServiceFactory:
    """Фабрика для создания сервисов"""
    
    @staticmethod
    def create_auth_service() -> 'AuthService':
        return get_container().get(AuthService)
    
    @staticmethod
    def create_content_service() -> 'ContentService':
        return get_container().get(ContentService)
    
    @staticmethod
    def create_task_service() -> 'TaskService':
        return get_container().get(TaskService)
    
    @staticmethod
    def create_theory_service() -> 'TheoryService':
        return get_container().get(TheoryService)
    
    @staticmethod
    def create_progress_service() -> 'ProgressService':
        return get_container().get(ProgressService)
    
    @staticmethod
    def create_stats_service() -> 'StatsService':
        return get_container().get(StatsService)
    
    @staticmethod
    def create_code_editor_service() -> 'CodeEditorService':
        return get_container().get(CodeEditorService)
    
    @staticmethod
    def create_code_executor_service() -> 'EnhancedCodeExecutorService':
        return get_container().get(EnhancedCodeExecutorService)
    
    @staticmethod
    def create_ai_test_generator_service() -> 'AITestGeneratorService':
        return get_container().get(AITestGeneratorService)
    
    @staticmethod
    def create_mindmap_service() -> 'MindMapService':
        return get_container().get(MindMapService)


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