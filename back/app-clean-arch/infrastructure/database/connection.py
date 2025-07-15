"""Подключение к базе данных"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import new_settings

# Создание engine с новой конфигурацией
engine = create_engine(
    new_settings.database.url,
    echo=new_settings.database.echo,
    pool_size=new_settings.database.pool_size,
    max_overflow=new_settings.database.max_overflow,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовая модель
Base = declarative_base()


# Зависимость для получения сессии базы данных
def get_db():
    """Получение сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
