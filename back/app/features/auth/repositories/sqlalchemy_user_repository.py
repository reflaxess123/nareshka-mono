"""Реализация репозитория пользователей для SQLAlchemy"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.features.auth.repositories.user_repository import UserRepository
from app.shared.models.user_models import User


class SQLAlchemyUserRepository(UserRepository):
    """Реализация репозитория пользователей для SQLAlchemy"""

    def __init__(self):
        pass

    async def get_by_id(self, id: int, session: Session = None) -> Optional[User]:
        """Получить пользователя по ID"""
        if session is None:
            from app.shared.database.base import db_manager

            with db_manager.get_session() as session:
                return session.query(User).filter(User.id == id).first()
        return session.query(User).filter(User.id == id).first()

    async def get_by_email(self, email: str, session: Session = None) -> Optional[User]:
        """Получить пользователя по email"""
        if session is None:
            from app.shared.database.connection import get_db

            db_gen = get_db()
            session = next(db_gen)
            try:
                return session.query(User).filter(User.email == email).first()
            finally:
                db_gen.close()
        return session.query(User).filter(User.email == email).first()

    async def get_all(
        self, limit: int = 100, offset: int = 0, session: Session = None
    ) -> List[User]:
        """Получить всех пользователей с пагинацией"""
        if session is None:
            from app.shared.database.base import db_manager

            with db_manager.get_session() as session:
                return session.query(User).offset(offset).limit(limit).all()
        return session.query(User).offset(offset).limit(limit).all()

    async def create(self, entity: User, session: Session = None) -> User:
        """Создать пользователя"""
        if session is None:
            from app.shared.database.base import db_manager

            with db_manager.get_session() as session:
                session.add(entity)
                session.flush()  # Получаем ID без commit
                session.commit()  # Коммитим изменения
                session.refresh(
                    entity
                )  # Обновляем объект после коммита для избежания DetachedInstanceError
                return entity
        session.add(entity)
        session.flush()  # Получаем ID без commit
        return entity

    async def update(self, entity: User, session: Session = None) -> User:
        """Обновить пользователя"""
        if session is None:
            from app.shared.database.base import db_manager

            with db_manager.get_session() as session:
                # Получаем существующий объект
                existing_user = session.query(User).filter(User.id == entity.id).first()
                if not existing_user:
                    raise ValueError(f"User with id {entity.id} not found")

                # Обновляем данные
                existing_user.email = entity.email
                existing_user.password = entity.password
                existing_user.role = entity.role
                existing_user.updatedAt = entity.updatedAt
                existing_user.totalTasksSolved = entity.totalTasksSolved
                existing_user.lastActivityDate = entity.lastActivityDate
                session.commit()
                return existing_user

        # Получаем существующий объект
        existing_user = session.query(User).filter(User.id == entity.id).first()
        if not existing_user:
            raise ValueError(f"User with id {entity.id} not found")

        # Обновляем данные
        existing_user.email = entity.email
        existing_user.password = entity.password
        existing_user.role = entity.role
        existing_user.updatedAt = entity.updatedAt
        existing_user.totalTasksSolved = entity.totalTasksSolved
        existing_user.lastActivityDate = entity.lastActivityDate

        return existing_user

    async def delete(self, id: int, session: Session = None) -> bool:
        """Удалить пользователя"""
        if session is None:
            from app.shared.database.base import db_manager

            with db_manager.get_session() as session:
                user = session.query(User).filter(User.id == id).first()
                if user:
                    session.delete(user)
                    session.commit()
                    return True
                return False
        user = session.query(User).filter(User.id == id).first()
        if user:
            session.delete(user)
            return True
        return False

    async def exists(self, id: int, session: Session = None) -> bool:
        """Проверить существование пользователя"""
        if session is None:
            from app.shared.database.base import db_manager

            with db_manager.get_session() as session:
                return session.query(User).filter(User.id == id).first() is not None
        return session.query(User).filter(User.id == id).first() is not None

    async def email_exists(self, email: str, session: Session = None) -> bool:
        """Проверить существование email"""
        if session is None:
            from app.shared.database.base import db_manager

            session_obj = db_manager.SessionLocal()
            try:
                return (
                    session_obj.query(User).filter(User.email == email).first()
                    is not None
                )
            finally:
                session_obj.close()
        return session.query(User).filter(User.email == email).first() is not None
