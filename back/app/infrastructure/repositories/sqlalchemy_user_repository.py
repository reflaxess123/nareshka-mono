"""Реализация репозитория пользователей для SQLAlchemy"""

from typing import List, Optional
from sqlalchemy.orm import Session

from ...domain.repositories.user_repository import UserRepository
from ..models.user_models import User


class SQLAlchemyUserRepository(UserRepository):
    """Реализация репозитория пользователей для SQLAlchemy"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def get_by_id(self, id: str) -> Optional[User]:
        """Получить пользователя по ID"""
        return self.session.query(User).filter(User.id == int(id)).first()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        return self.session.query(User).filter(User.email == email).first()
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Получить всех пользователей с пагинацией"""
        return self.session.query(User).offset(offset).limit(limit).all()
    
    async def create(self, entity: User) -> User:
        """Создать пользователя"""
        self.session.add(entity)
        self.session.flush()  # Получаем ID без commit
        return entity
    
    async def update(self, entity: User) -> User:
        """Обновить пользователя"""
        # Получаем существующий объект
        existing_user = self.session.query(User).filter(User.id == int(entity.id)).first()
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
    
    async def delete(self, id: str) -> bool:
        """Удалить пользователя"""
        user = self.session.query(User).filter(User.id == int(id)).first()
        if user:
            self.session.delete(user)
            return True
        return False
    
    async def exists(self, id: str) -> bool:
        """Проверить существование пользователя"""
        return self.session.query(User).filter(User.id == int(id)).first() is not None
    
    async def email_exists(self, email: str) -> bool:
        """Проверить существование email"""
        return self.session.query(User).filter(User.email == email).first() is not None 