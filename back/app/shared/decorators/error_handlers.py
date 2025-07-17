"""
Декораторы для унифицированной обработки ошибок в API роутерах
"""

from functools import wraps
from typing import Callable, Any, Type, Dict, Optional
from fastapi import HTTPException, status
from app.core.logging import get_logger
from app.shared.exceptions.base import (
    BaseAppException,
    DatabaseException,
    ResourceNotFoundException,
    ResourceConflictException,
    ValidationException,
    AuthenticationException,
    AuthorizationException
)

logger = get_logger(__name__)


def handle_api_errors(
    operation_name: str,
    default_error_message: str = "Operation failed",
    error_mapping: Optional[Dict[Type[Exception], tuple]] = None
):
    """
    Декоратор для унифицированной обработки ошибок в API роутерах
    
    Args:
        operation_name: Название операции для логирования
        default_error_message: Сообщение по умолчанию для неизвестных ошибок
        error_mapping: Дополнительное отображение исключений на HTTP статусы
    
    Usage:
        @handle_api_errors("create_user", "Failed to create user")
        async def create_user_endpoint(request: CreateUserRequest):
            # Логика создания пользователя
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Логирование начала операции
                logger.info(f"Starting {operation_name}", extra={
                    "operation": operation_name,
                    "function": func.__name__
                })
                
                # Выполнение основной логики
                result = await func(*args, **kwargs)
                
                # Логирование успешного завершения
                logger.info(f"Successfully completed {operation_name}", extra={
                    "operation": operation_name,
                    "function": func.__name__
                })
                
                return result
                
            except BaseAppException as e:
                # Обработка наших кастомных исключений
                logger.warning(f"API exception in {operation_name}: {e.message}", extra={
                    "operation": operation_name,
                    "function": func.__name__,
                    "error_type": type(e).__name__,
                    "error_message": e.message
                })
                raise HTTPException(
                    status_code=e.status_code,
                    detail=e.user_message
                )
                
            except ResourceNotFoundException as e:
                logger.warning(f"Resource not found in {operation_name}: {str(e)}", extra={
                    "operation": operation_name,
                    "function": func.__name__
                })
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=str(e)
                )
                
            except ResourceConflictException as e:
                logger.warning(f"Resource conflict in {operation_name}: {str(e)}", extra={
                    "operation": operation_name,
                    "function": func.__name__
                })
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=str(e)
                )
                
            except ValidationException as e:
                logger.warning(f"Validation error in {operation_name}: {str(e)}", extra={
                    "operation": operation_name,
                    "function": func.__name__
                })
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
                
            except AuthenticationException as e:
                logger.warning(f"Authentication error in {operation_name}: {str(e)}", extra={
                    "operation": operation_name,
                    "function": func.__name__
                })
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=str(e)
                )
                
            except AuthorizationException as e:
                logger.warning(f"Authorization error in {operation_name}: {str(e)}", extra={
                    "operation": operation_name,
                    "function": func.__name__
                })
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=str(e)
                )
                
            except DatabaseException as e:
                logger.error(f"Database error in {operation_name}: {str(e)}", extra={
                    "operation": operation_name,
                    "function": func.__name__
                })
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database operation failed"
                )
                
            except Exception as e:
                # Обработка дополнительных исключений из error_mapping
                if error_mapping:
                    for exc_type, (status_code, message) in error_mapping.items():
                        if isinstance(e, exc_type):
                            logger.warning(f"Mapped exception in {operation_name}: {str(e)}", extra={
                                "operation": operation_name,
                                "function": func.__name__,
                                "error_type": type(e).__name__
                            })
                            raise HTTPException(
                                status_code=status_code,
                                detail=message
                            )
                
                # Обработка всех остальных исключений
                logger.error(f"Unexpected error in {operation_name}: {str(e)}", extra={
                    "operation": operation_name,
                    "function": func.__name__,
                    "error_type": type(e).__name__
                }, exc_info=True)
                
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=default_error_message
                )
        
        return wrapper
    return decorator


def handle_sync_api_errors(
    operation_name: str,
    default_error_message: str = "Operation failed",
    error_mapping: Optional[Dict[Type[Exception], tuple]] = None
):
    """
    Декоратор для унифицированной обработки ошибок в синхронных API роутерах
    
    Args:
        operation_name: Название операции для логирования
        default_error_message: Сообщение по умолчанию для неизвестных ошибок
        error_mapping: Дополнительное отображение исключений на HTTP статусы
    
    Usage:
        @handle_sync_api_errors("get_user", "Failed to get user")
        def get_user_endpoint(user_id: int):
            # Логика получения пользователя
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Логирование начала операции
                logger.info(f"Starting {operation_name}", extra={
                    "operation": operation_name,
                    "function": func.__name__
                })
                
                # Выполнение основной логики
                result = func(*args, **kwargs)
                
                # Логирование успешного завершения
                logger.info(f"Successfully completed {operation_name}", extra={
                    "operation": operation_name,
                    "function": func.__name__
                })
                
                return result
                
            except BaseAppException as e:
                # Обработка наших кастомных исключений
                logger.warning(f"API exception in {operation_name}: {e.message}", extra={
                    "operation": operation_name,
                    "function": func.__name__,
                    "error_type": type(e).__name__,
                    "error_message": e.message
                })
                raise HTTPException(
                    status_code=e.status_code,
                    detail=e.user_message
                )
                
            except ResourceNotFoundException as e:
                logger.warning(f"Resource not found in {operation_name}: {str(e)}", extra={
                    "operation": operation_name,
                    "function": func.__name__
                })
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=str(e)
                )
                
            except ResourceConflictException as e:
                logger.warning(f"Resource conflict in {operation_name}: {str(e)}", extra={
                    "operation": operation_name,
                    "function": func.__name__
                })
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=str(e)
                )
                
            except ValidationException as e:
                logger.warning(f"Validation error in {operation_name}: {str(e)}", extra={
                    "operation": operation_name,
                    "function": func.__name__
                })
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
                
            except AuthenticationException as e:
                logger.warning(f"Authentication error in {operation_name}: {str(e)}", extra={
                    "operation": operation_name,
                    "function": func.__name__
                })
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=str(e)
                )
                
            except AuthorizationException as e:
                logger.warning(f"Authorization error in {operation_name}: {str(e)}", extra={
                    "operation": operation_name,
                    "function": func.__name__
                })
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=str(e)
                )
                
            except DatabaseException as e:
                logger.error(f"Database error in {operation_name}: {str(e)}", extra={
                    "operation": operation_name,
                    "function": func.__name__
                })
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database operation failed"
                )
                
            except Exception as e:
                # Обработка дополнительных исключений из error_mapping
                if error_mapping:
                    for exc_type, (status_code, message) in error_mapping.items():
                        if isinstance(e, exc_type):
                            logger.warning(f"Mapped exception in {operation_name}: {str(e)}", extra={
                                "operation": operation_name,
                                "function": func.__name__,
                                "error_type": type(e).__name__
                            })
                            raise HTTPException(
                                status_code=status_code,
                                detail=message
                            )
                
                # Обработка всех остальных исключений
                logger.error(f"Unexpected error in {operation_name}: {str(e)}", extra={
                    "operation": operation_name,
                    "function": func.__name__,
                    "error_type": type(e).__name__
                }, exc_info=True)
                
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=default_error_message
                )
        
        return wrapper
    return decorator


# Специализированные декораторы для часто используемых операций

def handle_create_errors(resource_name: str):
    """Декоратор для обработки ошибок создания ресурсов"""
    return handle_api_errors(
        operation_name=f"create_{resource_name}",
        default_error_message=f"Failed to create {resource_name}"
    )


def handle_update_errors(resource_name: str):
    """Декоратор для обработки ошибок обновления ресурсов"""
    return handle_api_errors(
        operation_name=f"update_{resource_name}",
        default_error_message=f"Failed to update {resource_name}"
    )


def handle_delete_errors(resource_name: str):
    """Декоратор для обработки ошибок удаления ресурсов"""
    return handle_api_errors(
        operation_name=f"delete_{resource_name}",
        default_error_message=f"Failed to delete {resource_name}"
    )


def handle_get_errors(resource_name: str):
    """Декоратор для обработки ошибок получения ресурсов"""
    return handle_sync_api_errors(
        operation_name=f"get_{resource_name}",
        default_error_message=f"Failed to get {resource_name}"
    )


def handle_list_errors(resource_name: str):
    """Декоратор для обработки ошибок получения списков ресурсов"""
    return handle_sync_api_errors(
        operation_name=f"list_{resource_name}",
        default_error_message=f"Failed to list {resource_name}"
    )