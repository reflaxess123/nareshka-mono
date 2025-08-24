"""Утилиты валидации для progress модуля"""

from typing import Any


def validate_positive_int(value: Any, field_name: str) -> int:
    """Валидация положительного числа"""
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field_name} должен быть положительным числом")
    return value


def validate_not_empty(value: Any, field_name: str) -> str:
    """Валидация непустой строки"""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} не может быть пустым")
    return value.strip()


def validate_limit(value: int, max_value: int = 100) -> int:
    """Валидация лимита результатов"""
    if value < 1 or value > max_value:
        raise ValueError(f"Лимит должен быть от 1 до {max_value}")
    return value


def validate_offset(value: int) -> int:
    """Валидация смещения"""
    if value < 0:
        raise ValueError("Смещение не может быть отрицательным")
    return value