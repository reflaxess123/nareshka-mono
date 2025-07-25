"""
Code Editor Feature

Модуль для работы с редактором кода и выполнением:
- Безопасное выполнение кода в Docker контейнерах
- Поддержка множественных языков программирования
- Сохранение и управление решениями пользователей
- Валидация кода и тест-кейсы
- Статистика выполнений
"""

# Router импортируется напрямую в main.py для избежания циклических импортов
from app.features.code_editor.services.code_editor_service import CodeEditorService
from app.features.code_editor.repositories.code_editor_repository import CodeEditorRepository

__all__ = [
    "CodeEditorService", 
    "CodeEditorRepository",
] 



