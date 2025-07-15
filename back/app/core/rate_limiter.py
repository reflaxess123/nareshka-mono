"""Rate limiting система с slowapi"""

from typing import Optional, Dict, Any
from fastapi import Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import redis
from functools import wraps

from app.core.settings import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Настройка Redis для rate limiting
try:
    redis_client = redis.from_url(
        settings.redis.url,
        max_connections=settings.redis.max_connections,
        decode_responses=True
    )
    redis_client.ping()
    logger.info("Redis connected for rate limiting")
except Exception as e:
    logger.warning(f"Redis not available, falling back to memory storage: {e}")
    redis_client = None


def get_user_id_from_request(request: Request) -> str:
    """Получить user_id из запроса для rate limiting"""
    # Пытаемся получить user_id из токена
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


# Создаем limiter с Redis или memory storage
if redis_client:
    limiter = Limiter(
        key_func=get_user_id_from_request,
        storage_uri=settings.redis.url,
        default_limits=["1000/minute", "10000/hour", "50000/day"]
    )
else:
    limiter = Limiter(
        key_func=get_user_id_from_request,
        default_limits=["1000/minute", "10000/hour", "50000/day"]
    )


# Whitelist для admin пользователей
ADMIN_WHITELIST = {
    "admin@nareshka.com",
    "127.0.0.1",
    "localhost"
}


def is_whitelisted(request: Request) -> bool:
    """Проверка whitelist для admin пользователей"""
    # Проверка по IP
    ip = get_remote_address(request)
    if ip in ADMIN_WHITELIST:
        return True
    
    # Проверка по API ключу
    api_key = get_api_key_from_request(request)
    if api_key and api_key == settings.proxyapi_key:
        return True
    
    # Проверка по user_id (если есть в токене)
    try:
        # Здесь должна быть логика проверки admin роли
        # Пока пропускаем
        pass
    except Exception:
        pass
    
    return False


def create_rate_limit_response(request: Request, response: Any) -> Dict[str, Any]:
    """Создать кастомный response для rate limit"""
    return {
        "error": "Rate limit exceeded",
        "message": "Too many requests. Please try again later.",
        "retry_after": getattr(response, "retry_after", 60),
        "limit": getattr(response, "limit", "1000/minute"),
        "remaining": getattr(response, "remaining", 0),
        "reset": getattr(response, "reset", None)
    }


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Кастомный handler для rate limit превышения"""
    logger.warning(
        "Rate limit exceeded",
        ip=get_remote_address(request),
        path=request.url.path,
        method=request.method,
        limit=exc.detail
    )
    
    # Создаем кастомный response
    response_data = create_rate_limit_response(request, exc)
    
    raise HTTPException(
        status_code=429,
        detail=response_data,
        headers={"Retry-After": str(getattr(exc, "retry_after", 60))}
    )


# Декораторы для разных типов rate limiting
def api_rate_limit(limit: str = "100/minute"):
    """Декоратор для API endpoints"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Получаем request из args
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if request and is_whitelisted(request):
                # Пропускаем rate limiting для whitelisted пользователей
                return await func(*args, **kwargs)
            
            # Применяем rate limiting
            return await limiter.limit(limit)(func)(*args, **kwargs)
        
        return wrapper
    return decorator


def auth_rate_limit(limit: str = "5/minute"):
    """Декоратор для auth endpoints (более строгий)"""
    return api_rate_limit(limit)


def upload_rate_limit(limit: str = "10/hour"):
    """Декоратор для upload endpoints"""
    return api_rate_limit(limit)


def expensive_operation_limit(limit: str = "2/minute"):
    """Декоратор для дорогих операций"""
    return api_rate_limit(limit)


# Middleware для автоматического rate limiting
class RateLimitMiddleware:
    """Middleware для автоматического rate limiting"""
    
    def __init__(self, app):
        self.app = app
        self.path_limits = {
            "/api/v2/auth/login": "5/minute",
            "/api/v2/auth/register": "3/minute",
            "/api/v2/code-editor/execute": "10/minute",
            "/api/v2/admin": "100/minute",
            "/api/v2/mindmap/generate": "5/minute",
        }
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope["path"]
            
            # Проверяем, нужно ли применять rate limiting
            if path in self.path_limits:
                # Здесь можно добавить логику проверки rate limit
                # Пока просто логируем
                logger.debug(f"Rate limit check for {path}")
        
        await self.app(scope, receive, send)


# Проверка health check для rate limiter
def rate_limiter_health_check() -> Dict[str, Any]:
    """Health check для rate limiter"""
    try:
        if redis_client:
            redis_client.ping()
            return {
                "status": "healthy",
                "storage": "redis",
                "redis_connected": True
            }
        else:
            return {
                "status": "healthy",
                "storage": "memory",
                "redis_connected": False
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Статистика rate limiting
def get_rate_limit_stats(user_id: str) -> Dict[str, Any]:
    """Получить статистику rate limiting для пользователя"""
    try:
        if redis_client:
            # Получаем статистику из Redis
            stats = {}
            # Здесь можно добавить логику получения статистики
            return stats
        else:
            return {"error": "Memory storage, no stats available"}
    except Exception as e:
        logger.error(f"Error getting rate limit stats: {e}")
        return {"error": str(e)}


# Сброс rate limit для пользователя (для admin)
def reset_rate_limit(user_id: str) -> bool:
    """Сбросить rate limit для пользователя"""
    try:
        if redis_client:
            # Логика сброса rate limit
            keys = redis_client.keys(f"*{user_id}*")
            if keys:
                redis_client.delete(*keys)
                logger.info(f"Rate limit reset for user {user_id}")
                return True
        return False
    except Exception as e:
        logger.error(f"Error resetting rate limit: {e}")
        return False


def get_rate_limiter() -> Limiter:
    """Получить экземпляр rate limiter"""
    return limiter


# Экспорт основных компонентов
__all__ = [
    'limiter',
    'get_rate_limiter',
    'rate_limit_exceeded_handler',
    'api_rate_limit',
    'auth_rate_limit',
    'upload_rate_limit',
    'expensive_operation_limit',
    'RateLimitMiddleware',
    'rate_limiter_health_check',
    'get_rate_limit_stats',
    'reset_rate_limit'
] 


