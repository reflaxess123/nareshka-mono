"""Базовая модель и система транзакций"""

from datetime import datetime
from typing import Any, Dict, Optional, Type, TypeVar, Generic, Callable, List
from functools import wraps
from sqlalchemy import Column, DateTime, Integer, Boolean, String, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import asyncio
from contextlib import contextmanager

from app.core.logging import get_logger
from app.core.settings import settings

logger = get_logger(__name__)

# Создаем базовую модель
Base = declarative_base()

# Type для generic модели
T = TypeVar('T', bound='BaseModel')


class BaseModel(Base):
    """Базовая модель для всех таблиц"""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать модель в словарь"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Создать модель из словаря"""
        return cls(**data)
    
    def soft_delete(self) -> None:
        """Мягкое удаление записи"""
        self.is_deleted = True
        self.updated_at = datetime.utcnow()
        logger.info(f"Soft deleted {self.__class__.__name__}", record_id=self.id)
    
    def restore(self) -> None:
        """Восстановить мягко удаленную запись"""
        self.is_deleted = False
        self.updated_at = datetime.utcnow()
        logger.info(f"Restored {self.__class__.__name__}", record_id=self.id)


class DatabaseManager:
    """Менеджер для работы с базой данных"""
    
    def __init__(self, database_url: str):
        from sqlalchemy import create_engine
        
        self.engine = create_engine(
            database_url,
            echo=settings.database.echo,
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
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


# Глобальный менеджер БД
db_manager = DatabaseManager(settings.database.url)


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
        if 'session' in kwargs:
            # Если session уже есть, используем её
            return func(*args, **kwargs)
        
        # Создаем новую транзакцию
        with db_manager.get_transaction() as session:
            kwargs['session'] = session
            return func(*args, **kwargs)
    
    return wrapper


def async_transactional(func: Callable) -> Callable:
    """
    Декоратор для выполнения async функции в транзакции
    
    Использование:
    @async_transactional
    async def create_user(name: str) -> User:
        # Код будет выполнен в транзакции
        pass
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Проверяем, есть ли уже session в kwargs
        if 'session' in kwargs:
            # Если session уже есть, используем её
            return await func(*args, **kwargs)
        
        # Создаем новую транзакцию в thread pool
        def run_in_transaction():
            with db_manager.get_transaction() as session:
                kwargs['session'] = session
                return func(*args, **kwargs)
        
        # Выполняем в отдельном thread
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, run_in_transaction)
    
    return wrapper


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


# Базовый репозиторий
class BaseRepository(Generic[T]):
    """Базовый репозиторий для работы с моделями"""
    
    def __init__(self, model: Type[T]):
        self.model = model
    
    def get_by_id(self, session: Session, id: int) -> Optional[T]:
        """Получить запись по ID"""
        return session.query(self.model).filter(
            self.model.id == id,
            self.model.is_deleted == False
        ).first()
    
    def get_all(self, session: Session, skip: int = 0, limit: int = 100) -> List[T]:
        """Получить все записи"""
        return session.query(self.model).filter(
            self.model.is_deleted == False
        ).offset(skip).limit(limit).all()
    
    def create(self, session: Session, obj_in: Dict[str, Any]) -> T:
        """Создать запись"""
        db_obj = self.model(**obj_in)
        session.add(db_obj)
        session.flush()
        logger.info(f"Created {self.model.__name__}", record_id=db_obj.id)
        return db_obj
    
    def update(self, session: Session, id: int, obj_in: Dict[str, Any]) -> Optional[T]:
        """Обновить запись"""
        db_obj = self.get_by_id(session, id)
        if db_obj:
            for field, value in obj_in.items():
                setattr(db_obj, field, value)
            db_obj.updated_at = datetime.utcnow()
            session.flush()
            logger.info(f"Updated {self.model.__name__}", record_id=db_obj.id)
        return db_obj
    
    def delete(self, session: Session, id: int) -> bool:
        """Мягкое удаление записи"""
        db_obj = self.get_by_id(session, id)
        if db_obj:
            db_obj.soft_delete()
            session.flush()
            return True
        return False
    
    def hard_delete(self, session: Session, id: int) -> bool:
        """Жесткое удаление записи"""
        db_obj = self.get_by_id(session, id)
        if db_obj:
            session.delete(db_obj)
            session.flush()
            logger.info(f"Hard deleted {self.model.__name__}", record_id=id)
            return True
        return False
    
    def count(self, session: Session) -> int:
        """Подсчитать количество записей"""
        return session.query(self.model).filter(
            self.model.is_deleted == False
        ).count()


# Экспорт для обратной совместимости
def get_db():
    """Для обратной совместимости с FastAPI Depends"""
    yield from get_db_session() 


