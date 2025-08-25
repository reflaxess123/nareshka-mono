"""
Dependency Injection система
"""

from .container import (
    DIContainer,
    configure_container,
    create_service_dependency,
    create_test_container,
    get_container,
    setup_di_container,
)

__all__ = [
    "DIContainer",
    "get_container",
    "configure_container",
    "create_service_dependency",
    "setup_di_container",
    "create_test_container",
]
