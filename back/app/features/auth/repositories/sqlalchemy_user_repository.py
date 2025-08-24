"""Реализация репозитория пользователей для SQLAlchemy"""

from typing import Optional

from sqlalchemy.orm import Session

from app.features.auth.repositories.user_repository import UserRepository
from app.shared.models.user_models import User


class SQLAlchemyUserRepository(UserRepository):
    """Реализация репозитория пользователей для SQLAlchemy"""

    def __init__(self):
        pass

    def _get_session(self, session: Session = None) -> Session:
        """Получить сессию БД - единый способ"""
        if session is not None:
            return session
            
        from app.shared.database import get_session
        return next(get_session())

    def _execute_with_session(self, operation, session: Session = None):
        """Выполнить операцию с автоматическим управлением сессией"""
        if session is not None:
            return operation(session)
        
        from app.shared.database import get_session
        db_session = next(get_session())
        try:
            return operation(db_session)
        finally:
            db_session.close()

    async def get_by_id(self, id: int, session: Session = None) -> Optional[User]:
        """Получить пользователя по ID"""
        def operation(s: Session):
            return s.query(User).filter(User.id == id).first()
        
        return self._execute_with_session(operation, session)

    async def get_by_email(self, email: str, session: Session = None) -> Optional[User]:
        """Получить пользователя по email"""
        def operation(s: Session):
            return s.query(User).filter(User.email == email).first()
        
        return self._execute_with_session(operation, session)

    async def create(self, entity: User, session: Session = None) -> User:
        """Создать пользователя"""
        def operation(s: Session):
            s.add(entity)
            s.flush()  # Получаем ID без commit
            s.commit()  # Коммитим изменения
            s.refresh(entity)  # Обновляем объект после коммита
            return entity
        
        return self._execute_with_session(operation, session)

    async def email_exists(self, email: str, session: Session = None) -> bool:
        """Проверить существование email"""
        def operation(s: Session):
            return s.query(User).filter(User.email == email).first() is not None
        
        return self._execute_with_session(operation, session)