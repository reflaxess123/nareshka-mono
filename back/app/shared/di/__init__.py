"""
Dependency Injection система
"""

from .container import (
    DIContainer,
    get_container,
    configure_container,
    inject,
    create_service_dependency,
    ServiceFactory,
    setup_di_container,
    create_test_container
)

__all__ = [
    "DIContainer",
    "get_container",
    "configure_container",
    "inject",
    "create_service_dependency",
    "ServiceFactory",
    "setup_di_container",
    "create_test_container"
]