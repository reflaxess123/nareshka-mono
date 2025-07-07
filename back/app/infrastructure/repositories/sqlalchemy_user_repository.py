"""Реализация репозитория пользователей для SQLAlchemy"""

from typing import List, Optional
from sqlalchemy.orm import Session

from ...domain.entities.user import User as DomainUser
from ...domain.repositories.user_repository import UserRepository
from ..models.user_models import User as InfraUser
from ..mappers.user_mapper import UserMapper


class SQLAlchemyUserRepository(UserRepository):
    """Реализация репозитория пользователей для SQLAlchemy"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def get_by_id(self, id: str) -> Optional[DomainUser]:
        """Получить пользователя по ID"""
        infra_user = self.session.query(InfraUser).filter(InfraUser.id == int(id)).first()
        return UserMapper.to_domain(infra_user) if infra_user else None
    
    async def get_by_email(self, email: str) -> Optional[DomainUser]:
        """Получить пользователя по email"""
        infra_user = self.session.query(InfraUser).filter(InfraUser.email == email).first()
        return UserMapper.to_domain(infra_user) if infra_user else None
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[DomainUser]:
        """Получить всех пользователей с пагинацией"""
        infra_users = self.session.query(InfraUser).offset(offset).limit(limit).all()
        return UserMapper.to_domain_list(infra_users)
    
    async def create(self, entity: DomainUser) -> DomainUser:
        """Создать пользователя"""
        infra_user = UserMapper.to_infrastructure(entity)
        self.session.add(infra_user)
        self.session.flush()  # Получаем ID без commit
        return UserMapper.to_domain(infra_user)
    
    async def update(self, entity: DomainUser) -> DomainUser:
        """Обновить пользователя"""
        # Получаем существующий Infrastructure объект
        infra_user = self.session.query(InfraUser).filter(InfraUser.id == int(entity.id)).first()
        if not infra_user:
            raise ValueError(f"User with id {entity.id} not found")
        
        # Обновляем данные
        updated_infra_user = UserMapper.update_infrastructure_from_domain(infra_user, entity)
        return UserMapper.to_domain(updated_infra_user)
    
    async def delete(self, id: str) -> bool:
        """Удалить пользователя"""
        infra_user = self.session.query(InfraUser).filter(InfraUser.id == int(id)).first()
        if infra_user:
            self.session.delete(infra_user)
            return True
        return False
    
    async def exists(self, id: str) -> bool:
        """Проверить существование пользователя"""
        return self.session.query(InfraUser).filter(InfraUser.id == int(id)).first() is not None
    
    async def email_exists(self, email: str) -> bool:
        """Проверить существование email"""
        return self.session.query(InfraUser).filter(InfraUser.email == email).first() is not None 