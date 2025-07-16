"""
Dependencies for Dependency Injection.
Updated for Feature-First architecture with backward compatibility.
"""

from typing import Optional
from functools import lru_cache

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

# New shared dependencies
from app.shared.database import get_session
from app.core.settings import Settings
from app.core.logging import get_logger
from app.core.rate_limiter import get_rate_limiter
from app.shared.utils import RequestContext

# Get logger instance
logger = get_logger(__name__)

# Backward compatibility imports (for gradual migration)
# Оставляем старый admin - не мигрируем (временно отключен)


from app.features.code_editor.services.ai_test_generator_service import AITestGeneratorService
from app.features.auth.services.auth_service import AuthService
from app.features.code_editor.services.code_editor_service import CodeEditorService
from app.features.code_editor.services.code_executor_service import CodeExecutorService
from app.features.content.services.content_service import ContentService
from app.features.mindmap.services.mindmap_service import MindMapService
from app.features.mindmap.repositories.mindmap_repository import MindMapRepository
from app.features.progress.services.progress_service import ProgressService
from app.features.stats.services.stats_service import StatsService
from app.features.task.services.task_service import TaskService
from app.features.theory.services.theory_service import TheoryService
from app.shared.database.connection import get_db
from app.shared.models.user_models import User
from app.features.code_editor.repositories.code_editor_repository import CodeEditorRepository
from app.features.content.repositories.content_repository import ContentRepository
from app.features.mindmap.repositories.mindmap_repository import MindMapRepository
from app.features.progress.repositories.progress_repository import ProgressRepository
from app.features.stats.repositories.stats_repository import StatsRepository
from app.features.task.repositories.task_repository import TaskRepository
from app.features.theory.repositories.theory_repository import TheoryRepository
from app.features.auth.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository

from .auth_schemes import oauth2_scheme

logger = get_logger(__name__)


# ===== NEW SHARED DEPENDENCIES =====

@lru_cache()
def get_app_settings() -> Settings:
    """Get application settings (cached)."""
    return Settings()


def get_db_manager():
    """Get database manager - заглушка."""
    return None


def get_db_session() -> Session:
    """Get database session (new system)."""
    return get_session()


def get_request_context(request: Request) -> RequestContext:
    """Get request context for logging and tracking."""
    return RequestContext(request)


def get_rate_limiter_service():
    """Get rate limiter service."""
    return get_rate_limiter()


# ===== COMPATIBILITY LAYER =====


def get_content_service(db: Session = Depends(get_db)) -> ContentService:
    """Получение сервиса для работы с контентом"""
    content_repository = ContentRepository(db)
    return ContentService(content_repository)


def get_theory_service(db: Session = Depends(get_db)) -> TheoryService:
    """Получение сервиса для работы с теоретическими карточками"""
    theory_repository = TheoryRepository(db)
    return TheoryService(theory_repository)


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    """Получение сервиса для работы с заданиями"""
    task_repository = TaskRepository(db)
    return TaskService(task_repository)


def get_progress_service(db: Session = Depends(get_db)) -> ProgressService:
    """Получение сервиса для работы с прогрессом"""
    progress_repository = ProgressRepository(db)
    return ProgressService(progress_repository)


def get_code_editor_service(db: Session = Depends(get_db)) -> CodeEditorService:
    """Возвращает экземпляр CodeEditorService с зависимостями"""
    from app.features.code_editor.services.code_editor_service import CodeEditorService
    
    code_editor_repository = CodeEditorRepository()
    return CodeEditorService(code_editor_repository)


def get_stats_service(db: Session = Depends(get_db)) -> StatsService:
    """Получение сервиса для работы со статистикой"""
    stats_repository = StatsRepository(db)
    return StatsService(stats_repository)


def get_mindmap_service(db: Session = Depends(get_db)) -> MindMapService:
    """Получение сервиса для работы с mindmap"""
    mindmap_repository = MindMapRepository(db)
    return MindMapService(mindmap_repository)


def get_auth_service() -> AuthService:
    """Получение сервиса авторизации"""
    user_repository = SQLAlchemyUserRepository()
    return AuthService(user_repository)


# def get_admin_service(
#     db: Session = Depends(get_db), auth_service: AuthService = Depends(get_auth_service)
# ) -> AdminService:
#     """Получение сервиса для работы с админкой"""
#     admin_repository = AdminRepository(db)
#     return AdminService(admin_repository, auth_service)
# Admin временно отключен - не мигрируем


def get_ai_test_generator_service(
    db: Session = Depends(get_db),
) -> AITestGeneratorService:
    """Получение сервиса генерации тест-кейсов через AI"""
    content_repository = ContentRepository(db)
    task_repository = TaskRepository(db)
    return AITestGeneratorService(content_repository, task_repository)


def get_code_executor_service(db: Session = Depends(get_db)) -> CodeExecutorService:
    """Возвращает экземпляр CodeExecutorService с зависимостями"""
    from app.features.code_editor.services.code_executor_service import CodeExecutorService
    
    code_editor_repository = CodeEditorRepository()
    return CodeExecutorService(code_editor_repository)


async def get_current_user_optional(
    request: Request, auth_service: AuthService = Depends(get_auth_service)
) -> Optional[User]:
    """Получение текущего пользователя (опционально)"""
    try:
        session_id = request.cookies.get("session_id")
        logger.info(f"🔍 DEBUG: get_current_user_optional called", extra={
            "has_session_cookie": session_id is not None,
            "session_id_prefix": session_id[:10] + "..." if session_id else None,
            "url": str(request.url),
            "method": request.method
        })
        
        user = await auth_service.get_user_by_session(request)
        
        if user:
            logger.info(f"🔍 DEBUG: User found from session", extra={
                "user_id": user.id,
                "user_email": user.email,
                "session_id_prefix": session_id[:10] + "..." if session_id else None
            })
        else:
            logger.info(f"🔍 DEBUG: No user found from session")
            
        return user
    except HTTPException as e:
        logger.info(f"🔍 DEBUG: Auth failed in get_current_user_optional", extra={
            "error": str(e),
            "status_code": e.status_code
        })
        return None


async def get_current_user_id_optional(
    user: Optional[User] = Depends(get_current_user_optional),
) -> Optional[int]:
    """Получение ID текущего пользователя (опционально)"""
    return user.id if user else None


async def get_current_user_required(
    request: Request, 
    auth_service: AuthService = Depends(get_auth_service),
    request_context: RequestContext = Depends(get_request_context)
) -> User:
    """Get current user (required) with enhanced error handling."""
    try:
        user = await auth_service.get_user_by_session(request)
        if not user:
            logger.warning("Authentication required but no user found", extra={
                "client_ip": request_context.client_ip,
                "url": request_context.url
            })
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Authentication required"
            )
            
        logger.debug("User authenticated successfully", extra={
            "user_id": user.id,
            "username": getattr(user, 'username', 'unknown'),
            "client_ip": request_context.client_ip
        })
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Authentication service error", extra={
            "error": str(e),
            "client_ip": request_context.client_ip
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service unavailable"
        )


async def get_current_user_jwt(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """Get current user by JWT token with enhanced validation."""
    try:
        user = await auth_service.get_user_by_token(token)
        if not user:
            logger.warning("JWT authentication failed - invalid token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        logger.debug("JWT authentication successful", extra={
            "user_id": user.id,
            "username": getattr(user, 'username', 'unknown')
        })
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("JWT validation error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token validation failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_jwt_optional(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> Optional[User]:
    """Get current user by JWT token (optional)."""
    try:
        user = await auth_service.get_user_by_token(token)
        if user:
            logger.debug("Optional JWT authentication successful", extra={
                "user_id": user.id,
                "username": getattr(user, 'username', 'unknown')
            })
        return user
    except Exception as e:
        logger.debug("Optional JWT authentication failed", extra={"error": str(e)})
        return None


async def get_current_admin_jwt(
    current_user: User = Depends(get_current_user_jwt),
) -> User:
    """Check admin privileges (JWT) with enhanced validation."""
    is_admin = (
        getattr(current_user, 'role', None) == "ADMIN" or 
        getattr(current_user, 'is_admin', False)
    )
    
    if not is_admin:
        logger.warning("Admin access denied", extra={
            "user_id": current_user.id,
            "username": getattr(current_user, 'username', 'unknown'),
            "role": getattr(current_user, 'role', 'unknown')
        })
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
        
    logger.info("Admin access granted", extra={
        "user_id": current_user.id,
        "username": getattr(current_user, 'username', 'unknown')
    })
    
    return current_user


def get_current_admin_session(
    current_user: User = Depends(get_current_user_required),
) -> User:
    """Check admin privileges (session) with enhanced validation."""
    is_admin = (
        getattr(current_user, 'role', None) == "ADMIN" or 
        getattr(current_user, 'is_admin', False)
    )
    
    if not is_admin:
        logger.warning("Admin session access denied", extra={
            "user_id": current_user.id,
            "username": getattr(current_user, 'username', 'unknown'),
            "role": getattr(current_user, 'role', 'unknown')
        })
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
        
    logger.info("Admin session access granted", extra={
        "user_id": current_user.id,
        "username": getattr(current_user, 'username', 'unknown')
    })
    
    return current_user


# ===== NEW FEATURE-FIRST DEPENDENCIES =====

def get_correlation_id(request: Request) -> str:
    """Get or generate correlation ID for request tracking."""
    correlation_id = request.headers.get('x-correlation-id')
    if not correlation_id:
        import uuid
        correlation_id = str(uuid.uuid4())
    return correlation_id


async def log_request_middleware(
    request: Request,
    request_context: RequestContext = Depends(get_request_context),
    user: Optional[User] = Depends(get_current_user_optional)
):
    """Middleware for request logging."""
    logger.info("API request", extra={
        "method": request_context.method,
        "url": request_context.url,
        "client_ip": request_context.client_ip,
        "user_agent": request_context.user_agent,
        "user_id": user.id if user else None,
        "username": getattr(user, 'username', None) if user else None
    })


