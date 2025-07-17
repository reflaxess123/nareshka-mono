"""
Middleware для унифицированной авторизации в API роутерах
"""

from functools import wraps
from typing import Callable, Optional, Any
from fastapi import HTTPException, status, Depends
from app.core.logging import get_logger
from app.shared.models.user_models import User
# Избегаем циклических импортов - импортируем только типы

logger = get_logger(__name__)


def require_user_ownership(field_name: str = "user_id"):
    """
    Декоратор для проверки владения ресурсом
    
    Args:
        field_name: Имя поля в объекте запроса, содержащего ID пользователя
    
    Usage:
        @require_user_ownership("user_id")
        async def create_progress(request: CreateProgressRequest, current_user: User = Depends(get_current_user_required)):
            # Автоматически проверяется что request.user_id == current_user.id
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Получаем current_user из kwargs
            current_user = kwargs.get('current_user')
            if not current_user:
                logger.error("Current user not found in request", extra={
                    "function": func.__name__,
                    "field_name": field_name
                })
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Ищем объект запроса с полем user_id
            request_obj = None
            for arg in args:
                if hasattr(arg, field_name):
                    request_obj = arg
                    break
            
            if not request_obj:
                # Ищем в kwargs
                for key, value in kwargs.items():
                    if hasattr(value, field_name):
                        request_obj = value
                        break
            
            if not request_obj:
                logger.error(f"Request object with field '{field_name}' not found", extra={
                    "function": func.__name__,
                    "field_name": field_name
                })
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error"
                )
            
            # Проверяем владение ресурсом
            request_user_id = getattr(request_obj, field_name)
            if request_user_id != current_user.id:
                logger.warning("User ownership check failed", extra={
                    "function": func.__name__,
                    "field_name": field_name,
                    "current_user_id": current_user.id,
                    "request_user_id": request_user_id
                })
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Можно создавать только для себя"
                )
            
            logger.debug("User ownership check passed", extra={
                "function": func.__name__,
                "field_name": field_name,
                "user_id": current_user.id
            })
            
            # Выполняем основную функцию
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_admin_role():
    """
    Декоратор для проверки админских прав
    
    Usage:
        @require_admin_role()
        async def admin_endpoint(current_user: User = Depends(get_current_user_required)):
            # Автоматически проверяется что current_user имеет админские права
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Получаем current_user из kwargs
            current_user = kwargs.get('current_user')
            if not current_user:
                logger.error("Current user not found in admin check", extra={
                    "function": func.__name__
                })
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Проверяем админские права
            is_admin = (
                getattr(current_user, 'role', None) == "ADMIN" or 
                getattr(current_user, 'is_admin', False)
            )
            
            if not is_admin:
                logger.warning("Admin access denied", extra={
                    "function": func.__name__,
                    "user_id": current_user.id,
                    "username": getattr(current_user, 'username', 'unknown'),
                    "role": getattr(current_user, 'role', 'unknown')
                })
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin privileges required"
                )
            
            logger.debug("Admin access granted", extra={
                "function": func.__name__,
                "user_id": current_user.id,
                "username": getattr(current_user, 'username', 'unknown')
            })
            
            # Выполняем основную функцию
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_user_or_admin(field_name: str = "user_id"):
    """
    Декоратор для проверки владения ресурсом ИЛИ админских прав
    
    Args:
        field_name: Имя поля в объекте запроса, содержащего ID пользователя
    
    Usage:
        @require_user_or_admin("user_id")
        async def get_user_data(request: GetUserRequest, current_user: User = Depends(get_current_user_required)):
            # Проверяется что request.user_id == current_user.id ИЛИ current_user - админ
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Получаем current_user из kwargs
            current_user = kwargs.get('current_user')
            if not current_user:
                logger.error("Current user not found in user-or-admin check", extra={
                    "function": func.__name__,
                    "field_name": field_name
                })
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Проверяем админские права
            is_admin = (
                getattr(current_user, 'role', None) == "ADMIN" or 
                getattr(current_user, 'is_admin', False)
            )
            
            if is_admin:
                logger.debug("Admin access granted", extra={
                    "function": func.__name__,
                    "user_id": current_user.id,
                    "access_type": "admin"
                })
                return await func(*args, **kwargs)
            
            # Если не админ, проверяем владение ресурсом
            request_obj = None
            for arg in args:
                if hasattr(arg, field_name):
                    request_obj = arg
                    break
            
            if not request_obj:
                for key, value in kwargs.items():
                    if hasattr(value, field_name):
                        request_obj = value
                        break
            
            if not request_obj:
                logger.error(f"Request object with field '{field_name}' not found", extra={
                    "function": func.__name__,
                    "field_name": field_name
                })
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error"
                )
            
            # Проверяем владение ресурсом
            request_user_id = getattr(request_obj, field_name)
            if request_user_id != current_user.id:
                logger.warning("User-or-admin check failed", extra={
                    "function": func.__name__,
                    "field_name": field_name,
                    "current_user_id": current_user.id,
                    "request_user_id": request_user_id,
                    "is_admin": is_admin
                })
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
            
            logger.debug("User ownership check passed", extra={
                "function": func.__name__,
                "field_name": field_name,
                "user_id": current_user.id,
                "access_type": "owner"
            })
            
            # Выполняем основную функцию
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def optional_user_context():
    """
    Декоратор для добавления опционального пользовательского контекста
    
    Usage:
        @optional_user_context()
        async def public_endpoint(current_user: Optional[User] = Depends(get_current_user_optional)):
            # current_user может быть None, но функция получит дополнительный контекст
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Получаем current_user из kwargs
            current_user = kwargs.get('current_user')
            
            if current_user:
                logger.debug("User context available", extra={
                    "function": func.__name__,
                    "user_id": current_user.id,
                    "username": getattr(current_user, 'username', 'unknown')
                })
            else:
                logger.debug("Anonymous user context", extra={
                    "function": func.__name__
                })
            
            # Выполняем основную функцию
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


class AuthorizationHelper:
    """
    Вспомогательный класс для проверки авторизации
    """
    
    @staticmethod
    def check_user_ownership(user: User, resource_user_id: int) -> bool:
        """Проверка владения ресурсом"""
        return user.id == resource_user_id
    
    @staticmethod
    def check_admin_privileges(user: User) -> bool:
        """Проверка админских прав"""
        return (
            getattr(user, 'role', None) == "ADMIN" or 
            getattr(user, 'is_admin', False)
        )
    
    @staticmethod
    def check_user_or_admin(user: User, resource_user_id: int) -> bool:
        """Проверка владения ресурсом ИЛИ админских прав"""
        return (
            AuthorizationHelper.check_user_ownership(user, resource_user_id) or
            AuthorizationHelper.check_admin_privileges(user)
        )
    
    @staticmethod
    def raise_ownership_error():
        """Выбросить ошибку владения ресурсом"""
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Можно создавать только для себя"
        )
    
    @staticmethod
    def raise_admin_error():
        """Выбросить ошибку админских прав"""
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    @staticmethod
    def raise_access_denied():
        """Выбросить ошибку доступа"""
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )