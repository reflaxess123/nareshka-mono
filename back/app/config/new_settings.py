"""Импорт настроек из core/settings.py"""

from app.core.settings import settings as core_settings

# Для обратной совместимости
new_settings = core_settings
legacy_settings = core_settings



