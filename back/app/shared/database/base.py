"""Базовая модель и система транзакций"""

from contextlib import contextmanager
from functools import wraps
from typing import Callable, TypeVar

from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from app.core.logging import get_logger
from app.core.settings import settings

logger = get_logger(__name__)

from app.shared.database.models import BaseModel

Base = BaseModel

# Type для generic модели
T = TypeVar("T", bound="BaseModel")


class DatabaseManager:
    """Менеджер для работы с базой данных"""

    def __init__(self, database_url: str):
        from sqlalchemy import create_engine

        self.engine = create_engine(
            database_url,
            echo=settings.database_echo,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_pre_ping=True,
            pool_recycle=3600,
        )

        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    @contextmanager
    def get_session(self):
        """Получить сессию БД с автоматическим закрытием"""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    @contextmanager
    def get_transaction(self):
        """Получить транзакцию с автоматическим commit/rollback"""
        session = self.SessionLocal()
        try:
            session.begin()
            yield session
            session.commit()
            logger.debug("Transaction committed successfully")
        except Exception as e:
            session.rollback()
            logger.error(f"Transaction rolled back: {e}", exc_info=True)
            raise
        finally:
            session.close()

    def create_tables(self) -> None:
        """Создать все таблицы"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created")

    def drop_tables(self) -> None:
        """Удалить все таблицы"""
        Base.metadata.drop_all(bind=self.engine)
        logger.info("Database tables dropped")

    def health_check(self) -> bool:
        """Проверка состояния БД"""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


db_manager = DatabaseManager(settings.database_url)


def transactional(func: Callable) -> Callable:
    """
    Декоратор для выполнения функции в транзакции

    Использование:
    @transactional
    def create_user(name: str) -> User:
        # Код будет выполнен в транзакции
        pass
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Проверяем, есть ли уже session в kwargs
        if "session" in kwargs:
            # Если session уже есть, используем её
            return func(*args, **kwargs)

        # Создаем новую транзакцию
        with db_manager.get_transaction() as session:
            kwargs["session"] = session
            return func(*args, **kwargs)

    return wrapper


def async_transactional(func: Callable) -> Callable:
    """
    Декоратор для выполнения async функции в транзакции
    ВНИМАНИЕ: Этот декоратор предназначен для будущего использования с async ORM
    В текущей реализации с синхронным SQLAlchemy используйте обычный @transactional
    """
    logger.warning(
        f"async_transactional используется для {func.__name__}. "
        f"Рекомендуется использовать @transactional для синхронных функций."
    )

    return transactional(func)


# Dependency для получения сессии
def get_db_session() -> Session:
    """Dependency для получения сессии БД"""
    with db_manager.get_session() as session:
        yield session


# Dependency для получения транзакции
def get_db_transaction() -> Session:
    """Dependency для получения транзакции"""
    with db_manager.get_transaction() as session:
        yield session


# Экспорт для обратной совместимости
def get_db():
    """Для обратной совместимости с FastAPI Depends"""
    yield from get_db_session()
