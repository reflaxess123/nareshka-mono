"""Структурированное логирование с JSON форматом и correlation ID"""

import sys
import uuid
import logging
from typing import Optional, Dict, Any
from contextvars import ContextVar
import structlog
from pythonjsonlogger import jsonlogger

from app.core.settings import settings

# Context variable для correlation ID
correlation_id_ctx: ContextVar[str] = ContextVar('correlation_id', default='')
user_id_ctx: ContextVar[str] = ContextVar('user_id', default='')
request_id_ctx: ContextVar[str] = ContextVar('request_id', default='')


def set_correlation_id(correlation_id: str) -> None:
    """Установить correlation ID для текущего контекста"""
    correlation_id_ctx.set(correlation_id)


def get_correlation_id() -> str:
    """Получить correlation ID из контекста"""
    return correlation_id_ctx.get()


def set_user_id(user_id: str) -> None:
    """Установить user ID для текущего контекста"""
    user_id_ctx.set(user_id)


def get_user_id() -> str:
    """Получить user ID из контекста"""
    return user_id_ctx.get()


def set_request_id(request_id: str) -> None:
    """Установить request ID для текущего контекста"""
    request_id_ctx.set(request_id)


def get_request_id() -> str:
    """Получить request ID из контекста"""
    return request_id_ctx.get()


def add_correlation_id(_, __, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Добавить correlation ID в лог"""
    if correlation_id := get_correlation_id():
        event_dict['correlation_id'] = correlation_id
    if user_id := get_user_id():
        event_dict['user_id'] = user_id
    if request_id := get_request_id():
        event_dict['request_id'] = request_id
    return event_dict


def add_service_info(_, __, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Добавить информацию о сервисе"""
    event_dict.update({
        'service': settings.app_name,
        'version': settings.app_version,
        'environment': settings.app_environment,
    })
    return event_dict


def filter_sensitive_data(_, __, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Фильтровать чувствительные данные"""
    sensitive_keys = {
        'password', 'secret', 'token', 'key', 'authorization', 
        'secret_key', 'access_token', 'refresh_token', 'api_key'
    }
    
    for key in list(event_dict.keys()):
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            event_dict[key] = '[FILTERED]'
    
    return event_dict


class CustomJSONFormatter(jsonlogger.JsonFormatter):
    """Кастомный JSON форматер"""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)
        
        # Добавляем стандартные поля
        log_record['timestamp'] = record.created
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno
        
        # Добавляем контекстные поля
        if correlation_id := get_correlation_id():
            log_record['correlation_id'] = correlation_id
        if user_id := get_user_id():
            log_record['user_id'] = user_id
        if request_id := get_request_id():
            log_record['request_id'] = request_id
        
        # Добавляем информацию о сервисе
        log_record['service'] = settings.app_name
        log_record['version'] = settings.app_version
        log_record['environment'] = settings.app_environment


def setup_logging() -> None:
    """Настройка системы логирования"""
    
    # Настройка уровня логирования
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Очистка существующих handlers
    logging.root.handlers = []
    
    if settings.log_format == 'json':
        # JSON формат для продакшен
        formatter = CustomJSONFormatter(
            fmt='%(timestamp)s %(level)s %(logger)s %(module)s %(function)s %(line)d %(message)s'
        )
        
        # Настройка structlog для JSON
        structlog.configure(
            processors=[
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                add_correlation_id,
                add_service_info,
                filter_sensitive_data,
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
    else:
        # Текстовый формат для разработки
        formatter = logging.Formatter(
            fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Настройка structlog для текста
        structlog.configure(
            processors=[
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
                add_correlation_id,
                add_service_info,
                filter_sensitive_data,
                structlog.dev.ConsoleRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    
    # Настройка console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # Настройка root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # Настройка логгеров для библиотек
    logging.getLogger('uvicorn').setLevel(getattr(logging, settings.uvicorn_log_level.upper(), logging.INFO))
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('watchfiles').setLevel(getattr(logging, settings.watchfiles_log_level.upper(), logging.WARNING))
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
    
    # Отключаем избыточные логи
    logging.getLogger('multipart').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Получить структурированный логгер"""
    return structlog.get_logger(name)


def create_correlation_id() -> str:
    """Создать новый correlation ID"""
    return str(uuid.uuid4())


# Middleware для установки correlation ID
class CorrelationIdMiddleware:
    """Middleware для установки correlation ID для каждого запроса"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Создаем correlation ID для запроса
            correlation_id = create_correlation_id()
            set_correlation_id(correlation_id)
            
            # Устанавливаем request ID
            request_id = scope.get("headers", {}).get("x-request-id", correlation_id)
            set_request_id(request_id)
            
            # Логируем начало запроса
            logger = get_logger("request")
            logger.info(
                "Request started",
                method=scope["method"],
                path=scope["path"],
                query_string=scope.get("query_string", b"").decode(),
            )
        
        await self.app(scope, receive, send)


# Инициализация логирования при импорте
setup_logging()

# Экспорт для обратной совместимости
def init_default_logging():
    """Для обратной совместимости"""
    setup_logging()



