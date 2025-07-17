"""
Общие декораторы для приложения
"""

from .error_handlers import (
    handle_api_errors,
    handle_sync_api_errors,
    handle_create_errors,
    handle_update_errors,
    handle_delete_errors,
    handle_get_errors,
    handle_list_errors
)

__all__ = [
    "handle_api_errors",
    "handle_sync_api_errors", 
    "handle_create_errors",
    "handle_update_errors",
    "handle_delete_errors",
    "handle_get_errors",
    "handle_list_errors"
]