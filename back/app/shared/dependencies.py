"""
Dependencies for Dependency Injection.
Updated for Feature-First architecture with DI Container.
"""

from functools import lru_cache
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.rate_limiter import get_rate_limiter
from app.core.settings import Settings

from app.features.auth.services.auth_service import AuthService
from app.features.code_editor.services.ai_test_generator_service import AITestGeneratorService
from app.features.code_editor.services.code_editor_service import CodeEditorService
from app.features.code_editor.services.code_executor_service import CodeExecutorService
from app.features.content.services.content_service import ContentService
from app.features.mindmap.services.mindmap_service import MindMapService
from app.features.progress.services.progress_service import ProgressService
from app.features.stats.services.stats_service import StatsService
from app.features.task.services.task_service import TaskService
from app.features.theory.services.theory_service import TheoryService

# Database
from app.shared.database import get_session
from app.shared.database.connection import get_db

# DI Container
from app.shared.di import create_service_dependency

# Models
from app.shared.models.user_models import User

# Utils
from app.shared.utils import RequestContext

# OAuth2 scheme for JWT authentication
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v2/auth/login")


logger = get_logger(__name__)


# ===== NEW SHARED DEPENDENCIES =====


@lru_cache
def get_app_settings() -> Settings:
    """Get application settings (cached)."""
    return Settings()




def get_db_session() -> Session:
    """Get database session (new system)."""
    return get_session()


def get_request_context(request: Request) -> RequestContext:
    """Get request context for logging and tracking."""
    return RequestContext(request)


def get_rate_limiter_service():
    """Get rate limiter service."""
    return get_rate_limiter()



get_content_service = create_service_dependency(ContentService)
get_theory_service = create_service_dependency(TheoryService)
get_task_service = create_service_dependency(TaskService)
get_progress_service = create_service_dependency(ProgressService)
get_code_editor_service = create_service_dependency(CodeEditorService)
get_stats_service = create_service_dependency(StatsService)
get_mindmap_service = create_service_dependency(MindMapService)
get_auth_service = create_service_dependency(AuthService)
get_code_executor_service = create_service_dependency(CodeExecutorService)
get_ai_test_generator_service = create_service_dependency(AITestGeneratorService)



async def get_current_user_optional(
    request: Request, auth_service: AuthService = Depends(get_auth_service)
) -> Optional[User]:
    """Получение текущего пользователя (опционально)"""
    try:
        user = await auth_service.get_user_by_session(request)
        if user:
            logger.debug(
                "User authenticated via session",
                extra={"user_id": user.id, "email": user.email}
            )
        return user
    except HTTPException:
        return None


async def get_current_user_id_optional(
    user: Optional[User] = Depends(get_current_user_optional),
) -> Optional[int]:
    """Получение ID текущего пользователя (опционально)"""
    return user.id if user else None


async def get_current_user_required(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    request_context: RequestContext = Depends(get_request_context),
) -> User:
    """Get current user (required) with enhanced error handling."""
    try:
        user = await auth_service.get_user_by_session(request)
        if not user:
            logger.warning(
                "Authentication required but no user found",
                extra={
                    "client_ip": request_context.client_ip,
                    "url": request_context.url,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        logger.debug(
            "User authenticated successfully",
            extra={
                "user_id": user.id,
                "username": getattr(user, "username", "unknown"),
                "client_ip": request_context.client_ip,
            },
        )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Authentication service error",
            extra={"error": str(e), "client_ip": request_context.client_ip},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service unavailable",
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

        logger.debug(
            "JWT authentication successful",
            extra={
                "user_id": user.id,
                "username": getattr(user, "username", "unknown"),
            },
        )

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
            logger.debug(
                "Optional JWT authentication successful",
                extra={
                    "user_id": user.id,
                    "username": getattr(user, "username", "unknown"),
                },
            )
        return user
    except Exception as e:
        logger.debug("Optional JWT authentication failed", extra={"error": str(e)})
        return None

def get_current_admin_session(
    current_user: User = Depends(get_current_user_required),
) -> User:
    """Check admin privileges (session) with enhanced validation."""
    is_admin = getattr(current_user, "role", None) == "ADMIN" or getattr(
        current_user, "is_admin", False
    )

    if not is_admin:
        logger.warning(
            "Admin session access denied",
            extra={
                "user_id": current_user.id,
                "username": getattr(current_user, "username", "unknown"),
                "role": getattr(current_user, "role", "unknown"),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )

    logger.info(
        "Admin session access granted",
        extra={
            "user_id": current_user.id,
            "username": getattr(current_user, "username", "unknown"),
        },
    )

    return current_user


# ===== UTILITY DEPENDENCIES =====


def get_db_manager():
    """Get DatabaseManager instance for progress feature."""
    from app.shared.database.base import DatabaseManager
    from app.core.settings import settings

    return DatabaseManager(settings.database_url)


def get_correlation_id(request: Request) -> str:
    """Get or generate correlation ID for request tracking."""
    correlation_id = request.headers.get("x-correlation-id")
    if not correlation_id:
        import uuid

        correlation_id = str(uuid.uuid4())
    return correlation_id


