"""Зависимости для Dependency Injection"""

from typing import Generator, Optional
from fastapi import Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

from ..infrastructure.database.connection import get_db
from ..infrastructure.repositories.sqlalchemy_content_repository import SQLAlchemyContentRepository
from ..infrastructure.repositories.sqlalchemy_theory_repository import SQLAlchemyTheoryRepository
from ..infrastructure.repositories.sqlalchemy_task_repository import SQLAlchemyTaskRepository
from ..infrastructure.repositories.sqlalchemy_progress_repository import SQLAlchemyProgressRepository
from ..infrastructure.repositories.sqlalchemy_code_editor_repository import SQLAlchemyCodeEditorRepository
from ..infrastructure.repositories.sqlalchemy_stats_repository import SQLAlchemyStatsRepository
from ..infrastructure.repositories.sqlalchemy_mindmap_repository import SqlAlchemyMindMapRepository
from ..infrastructure.repositories.sqlalchemy_admin_repository import SQLAlchemyAdminRepository
from ..infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from ..application.services.content_service import ContentService
from ..application.services.theory_service import TheoryService
from ..application.services.task_service import TaskService
from ..application.services.progress_service import ProgressService
from ..application.services.code_editor_service import CodeEditorService
from ..application.services.stats_service import StatsService
from ..application.services.mindmap_service import MindMapService
from ..application.services.admin_service import AdminService
from ..application.services.auth_service import AuthService
from ..application.services.ai_test_generator_service import AITestGeneratorService
from ..application.services.code_executor_service import CodeExecutorService
from ..infrastructure.models.user_models import User
from .auth_schemes import oauth2_scheme


def get_content_service(
    db: Session = Depends(get_db)
) -> ContentService:
    """Получение сервиса для работы с контентом"""
    content_repository = SQLAlchemyContentRepository(db)
    return ContentService(content_repository)


def get_theory_service(
    db: Session = Depends(get_db)
) -> TheoryService:
    """Получение сервиса для работы с теоретическими карточками"""
    theory_repository = SQLAlchemyTheoryRepository(db)
    return TheoryService(theory_repository)


def get_task_service(
    db: Session = Depends(get_db)
) -> TaskService:
    """Получение сервиса для работы с заданиями"""
    task_repository = SQLAlchemyTaskRepository(db)
    return TaskService(task_repository)


def get_progress_service(
    db: Session = Depends(get_db)
) -> ProgressService:
    """Получение сервиса для работы с прогрессом"""
    progress_repository = SQLAlchemyProgressRepository(db)
    return ProgressService(progress_repository)


def get_code_editor_service(
    db: Session = Depends(get_db)
) -> CodeEditorService:
    """Получение сервиса для работы с редактором кода"""
    code_editor_repository = SQLAlchemyCodeEditorRepository(db)
    return CodeEditorService(code_editor_repository)


def get_stats_service(
    db: Session = Depends(get_db)
) -> StatsService:
    """Получение сервиса для работы со статистикой"""
    stats_repository = SQLAlchemyStatsRepository(db)
    return StatsService(stats_repository)


def get_mindmap_service(
    db: Session = Depends(get_db)
) -> MindMapService:
    """Получение сервиса для работы с mindmap"""
    mindmap_repository = SqlAlchemyMindMapRepository(db)
    return MindMapService(mindmap_repository)


def get_auth_service(
    db: Session = Depends(get_db)
) -> AuthService:
    """Получение сервиса авторизации"""
    user_repository = SQLAlchemyUserRepository(db)
    return AuthService(user_repository)


def get_admin_service(
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> AdminService:
    """Получение сервиса для работы с админкой"""
    admin_repository = SQLAlchemyAdminRepository(db)
    return AdminService(admin_repository, auth_service)


def get_ai_test_generator_service(
    db: Session = Depends(get_db)
) -> AITestGeneratorService:
    """Получение сервиса генерации тест-кейсов через AI"""
    content_repository = SQLAlchemyContentRepository(db)
    task_repository = SQLAlchemyTaskRepository(db)
    return AITestGeneratorService(content_repository, task_repository)


def get_code_executor_service(
    db: Session = Depends(get_db)
) -> CodeExecutorService:
    """Получение сервиса выполнения кода"""
    code_editor_repository = SQLAlchemyCodeEditorRepository(db)
    return CodeExecutorService(code_editor_repository)


async def get_current_user_optional(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[User]:
    """Получение текущего пользователя (опционально)"""
    try:
        return await auth_service.get_user_by_session(request)
    except HTTPException:
        return None


async def get_current_user_required(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Получение текущего пользователя (обязательно)"""
    return await auth_service.get_user_by_session(request)


async def get_current_user_jwt(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Получение текущего пользователя из JWT токена"""
    return await auth_service.get_user_by_token(token)


async def get_current_user_jwt_optional(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[User]:
    """Получение текущего пользователя из JWT токена (опционально)"""
    try:
        return await auth_service.get_user_by_token(token)
    except:
        return None


async def get_current_admin_jwt(
    current_user: User = Depends(get_current_user_jwt)
) -> User:
    """Получение текущего пользователя с проверкой роли админа"""
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    return current_user


def get_current_admin_session(
    current_user: User = Depends(get_current_user_required)
) -> User:
    """Получение текущего пользователя с проверкой роли админа (через сессию)"""
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    return current_user 