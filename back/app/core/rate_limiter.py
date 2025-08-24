"""Rate limiting система с slowapi"""

from typing import Any, Dict, Optional

import redis
from fastapi import HTTPException, Request
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.logging import get_logger
from app.core.settings import settings

logger = get_logger(__name__)

try:
    redis_client = redis.from_url(
        settings.redis_url,
        max_connections=settings.redis_max_connections,
        decode_responses=True,
    )
    redis_client.ping()
    logger.info("Redis connected for rate limiting")
except Exception as e:
    logger.warning(f"Redis not available, falling back to memory storage: {e}")
    redis_client = None


def get_user_id_from_request(request: Request) -> str:
    """Получить user_id из запроса для rate limiting"""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            # Здесь должна быть логика извлечения user_id из JWT
            # Для совместимости пока используем IP
            return get_remote_address(request)
        except Exception:
            pass

    # Fallback на IP адрес
    return get_remote_address(request)


def get_api_key_from_request(request: Request) -> Optional[str]:
    """Получить API ключ из запроса"""
    return request.headers.get("X-API-Key")


if redis_client:
    limiter = Limiter(
        key_func=get_user_id_from_request,
        storage_uri=settings.redis_url,
        default_limits=["1000/minute", "10000/hour", "50000/day"],
    )
else:
    limiter = Limiter(
        key_func=get_user_id_from_request,
        default_limits=["1000/minute", "10000/hour", "50000/day"],
    )


ADMIN_WHITELIST = {"admin@nareshka.com", "127.0.0.1", "localhost"}


def is_whitelisted(request: Request) -> bool:
    """Проверка whitelist для admin пользователей"""
    ip = get_remote_address(request)
    if ip in ADMIN_WHITELIST:
        return True

    api_key = get_api_key_from_request(request)
    if api_key and api_key == settings.proxyapi_key:
        return True

    return False


def create_rate_limit_response(request: Request, response: Any) -> Dict[str, Any]:
    """Создать кастомный response для rate limit"""
    return {
        "error": "Rate limit exceeded",
        "message": "Too many requests. Please try again later.",
        "retry_after": getattr(response, "retry_after", 60),
        "limit": getattr(response, "limit", "1000/minute"),
        "remaining": getattr(response, "remaining", 0),
        "reset": getattr(response, "reset", None),
    }


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Кастомный handler для rate limit превышения"""
    logger.warning(
        "Rate limit exceeded",
        ip=get_remote_address(request),
        path=request.url.path,
        method=request.method,
        limit=exc.detail,
    )

    response_data = create_rate_limit_response(request, exc)

    raise HTTPException(
        status_code=429,
        detail=response_data,
        headers={"Retry-After": str(getattr(exc, "retry_after", 60))},
    )


def get_rate_limiter() -> Limiter:
    """Получить экземпляр rate limiter"""
    return limiter


__all__ = [
    "limiter",
    "get_rate_limiter",
]
