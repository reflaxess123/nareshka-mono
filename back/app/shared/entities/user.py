"""
Shared User Entity - основная модель пользователя

Используется во всех features для ссылок на пользователя.
Модель без relationships для обеспечения изоляции features.
"""

from typing import Optional
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func

from app.shared.database import BaseModel, AuditMixin
from app.shared.types import UserRole as SharedUserRole
from app.core.logging import get_logger

logger = get_logger(__name__)

# User role enum for shared entity
class UserRole(str, Enum):
    """User role enum for shared entity."""
    GUEST = "GUEST"
    USER = "USER" 
    ADMIN = "ADMIN"

    # Compatibility with shared enum
    @classmethod
    def from_shared(cls, shared_role: SharedUserRole) -> 'UserRole':
        """Convert from shared UserRole to entity UserRole."""
        mapping = {
            SharedUserRole.GUEST: cls.GUEST,
            SharedUserRole.USER: cls.USER,
            SharedUserRole.ADMIN: cls.ADMIN,
            SharedUserRole.MODERATOR: cls.ADMIN  # Map moderator to admin for now
        }
        return mapping.get(shared_role, cls.USER)
    
    def to_shared(self) -> SharedUserRole:
        """Convert to shared UserRole."""
        mapping = {
            self.GUEST: SharedUserRole.GUEST,
            self.USER: SharedUserRole.USER,
            self.ADMIN: SharedUserRole.ADMIN
        }
        return mapping.get(self, SharedUserRole.USER)


class User(BaseModel, AuditMixin):
    """
    Shared User entity for cross-feature usage.
    
    This model is used by all features for user references.
    NO RELATIONSHIPS - features should use repositories for data access.
    """
    
    __tablename__ = "User"
    
    # Primary key (explicitly defined for clarity)
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Basic user information
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    
    # Legacy fields (for backward compatibility)
    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Activity tracking
    totalTasksSolved = Column(Integer, default=0, server_default="0", nullable=False)
    lastActivityDate = Column(DateTime, nullable=True)
    
    # Profile information (optional)
    username = Column(String(100), unique=True, nullable=True, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # Status flags
    is_active = Column("is_active", default=True, nullable=False)
    is_verified = Column("is_verified", default=False, nullable=False)
    
    # NO RELATIONSHIPS - для обеспечения изоляции features
    # Features должны использовать repositories для получения связанных данных
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"

    @property
    def is_admin(self) -> bool:
        """Проверка является ли пользователь администратором"""
        return self.role == UserRole.ADMIN

    @property 
    def is_user(self) -> bool:
        """Проверка является ли пользователь обычным пользователем"""
        return self.role == UserRole.USER

    @property
    def is_guest(self) -> bool:
        """Проверка является ли пользователь гостем"""
        return self.role == UserRole.GUEST

    @property
    def full_name(self) -> Optional[str]:
        """Полное имя пользователя"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return None

    @property
    def display_name(self) -> str:
        """Отображаемое имя пользователя"""
        return self.full_name or self.username or self.email.split('@')[0]

    def update_last_activity(self) -> None:
        """Обновление времени последней активности"""
        self.lastActivityDate = datetime.utcnow()

    def increment_tasks_solved(self) -> None:
        """
        Увеличение счётчика решённых задач
        
        ВНИМАНИЕ: Этот метод изменяет только модель в памяти.
        Для сохранения изменений нужно вызвать session.commit()
        """
        self.totalTasksSolved += 1

    def has_permission(self, permission: str) -> bool:
        """
        Проверка прав доступа пользователя
        
        Args:
            permission: строка с названием разрешения
            
        Returns:
            bool: True если у пользователя есть это разрешение
        """
        # Администратор имеет все права
        if self.is_admin:
            return True
            
        # Базовые права для авторизованных пользователей
        basic_permissions = {
            'view_content', 'solve_tasks', 'view_progress',
            'view_profile', 'update_profile'
        }
        
        if self.is_user and permission in basic_permissions:
            return True
            
        # Гости имеют только права на просмотр
        guest_permissions = {'view_content', 'view_public_tasks'}
        if self.is_guest and permission in guest_permissions:
            return True
            
        return False

    def to_public_dict(self) -> dict:
        """
        Преобразование модели в публичный словарь для API
        
        Исключает приватную информацию типа пароля
        """
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role.value,
            'display_name': self.display_name,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'totalTasksSolved': self.totalTasksSolved,
            'lastActivityDate': self.lastActivityDate.isoformat() if self.lastActivityDate else None,
            'createdAt': self.createdAt.isoformat() if self.createdAt else None,
        }

    class Config:
        """Pydantic configuration."""
        from_attributes = True
        use_enum_values = True 


