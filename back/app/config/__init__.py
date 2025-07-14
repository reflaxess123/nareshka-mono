"""Пакет конфигурации"""

from .new_settings import legacy_settings, new_settings

# Для обратной совместимости со старыми импортами
settings = legacy_settings

__all__ = ["new_settings", "settings"]



