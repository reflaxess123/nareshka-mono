"""Маппер для User entity"""

from typing import List, Optional
from datetime import datetime

from ...domain.entities.user import User as DomainUser
from ...domain.entities.enums import UserRole
from ..models.user_models import User as InfraUser


class UserMapper:
    """Маппер для конвертации User между domain и infrastructure слоями"""
    
    @staticmethod
    def to_domain(infra_user: InfraUser) -> DomainUser:
        """Конвертирует Infrastructure User в Domain User"""
        if not infra_user:
            return None
            
        return DomainUser(
            id=infra_user.id,
            email=infra_user.email,
            password=infra_user.password,
            role=UserRole(infra_user.role.value) if infra_user.role else UserRole.USER,
            createdAt=infra_user.createdAt,
            updatedAt=infra_user.updatedAt,
            totalTasksSolved=infra_user.totalTasksSolved,
            lastActivityDate=infra_user.lastActivityDate
        )
    
    @staticmethod
    def to_infrastructure(domain_user: DomainUser) -> InfraUser:
        """Конвертирует Domain User в Infrastructure User"""
        if not domain_user:
            return None
            
        return InfraUser(
            id=domain_user.id,
            email=domain_user.email,
            password=domain_user.password,
            role=domain_user.role,
            createdAt=domain_user.createdAt,
            updatedAt=domain_user.updatedAt,
            totalTasksSolved=domain_user.totalTasksSolved,
            lastActivityDate=domain_user.lastActivityDate
        )
    
    @staticmethod
    def to_domain_list(infra_users: List[InfraUser]) -> List[DomainUser]:
        """Конвертирует список Infrastructure Users в Domain Users"""
        if not infra_users:
            return []
        return [UserMapper.to_domain(user) for user in infra_users if user]
    
    @staticmethod
    def to_infrastructure_list(domain_users: List[DomainUser]) -> List[InfraUser]:
        """Конвертирует список Domain Users в Infrastructure Users"""
        if not domain_users:
            return []
        return [UserMapper.to_infrastructure(user) for user in domain_users if user]
    
    @staticmethod
    def update_infrastructure_from_domain(infra_user: InfraUser, domain_user: DomainUser) -> InfraUser:
        """Обновляет Infrastructure User данными из Domain User"""
        if not infra_user or not domain_user:
            return infra_user
            
        infra_user.email = domain_user.email
        infra_user.password = domain_user.password
        infra_user.role = domain_user.role
        infra_user.updatedAt = domain_user.updatedAt or datetime.utcnow()
        infra_user.totalTasksSolved = domain_user.totalTasksSolved
        infra_user.lastActivityDate = domain_user.lastActivityDate
        
        return infra_user 