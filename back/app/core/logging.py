"""Централизованная система логирования"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..config import new_settings


class ColoredFormatter(logging.Formatter):
    """Цветной форматтер для консольного вывода"""
    
    COLORS = {
        'DEBUG': '\033[94m',    # Синий
        'INFO': '\033[92m',     # Зеленый  
        'WARNING': '\033[93m',  # Желтый
        'ERROR': '\033[91m',    # Красный
        'CRITICAL': '\033[95m', # Пурпурный
        'ENDC': '\033[0m'       # Сброс цвета
    }

    def format(self, record):
        # Добавляем цвет для уровня логирования
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['ENDC']}"
        
        return super().format(record)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_console: bool = True
) -> None:
    """
    Настройка централизованного логирования
    
    Args:
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Путь к файлу логов (опционально)
        enable_console: Включить консольный вывод
    """
    
    # Получаем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Очищаем существующие обработчики
    root_logger.handlers.clear()
    
    # Формат логов
    log_format = "%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Консольный обработчик с цветами
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_formatter = ColoredFormatter(log_format, date_format)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # Файловый обработчик
    if log_file:
        # Создаем директорию для логов если не существует
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # В файл пишем все
        file_formatter = logging.Formatter(log_format, date_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Настройка логирования для внешних библиотек
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # Логгер для нашего приложения
    app_logger = logging.getLogger("nareshka")
    app_logger.info("Система логирования инициализирована")


def get_logger(name: str) -> logging.Logger:
    """
    Получить логгер для модуля
    
    Args:
        name: Имя модуля (обычно __name__)
        
    Returns:
        Настроенный логгер
    """
    return logging.getLogger(f"nareshka.{name}")


# Инициализация по умолчанию
def init_default_logging():
    """Инициализация логирования с настройками по умолчанию"""
    log_level = getattr(new_settings, 'log_level', 'INFO')
    
    # В development режиме логи в консоль и файл
    if getattr(new_settings, 'environment', 'development') == 'development':
        setup_logging(
            log_level=log_level,
            log_file="logs/nareshka.log",
            enable_console=True
        )
    else:
        # В production только в файл
        setup_logging(
            log_level=log_level,
            log_file="/var/log/nareshka/app.log",
            enable_console=False
        ) 