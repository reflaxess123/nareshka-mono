"""
Адаптерные слои для межмодульной коммуникации
"""

from .inter_module_adapter import (
    ContentAdapter,
    ContentInfo,
    ContentProviderProtocol,
    ContentRepositoryProvider,
    InterModuleFacade,
    TaskAdapter,
    TaskInfo,
    TaskProviderProtocol,
    TaskRepositoryProvider,
    UserAdapter,
    UserInfo,
    UserProviderProtocol,
    get_inter_module_facade,
    setup_inter_module_adapters,
)

__all__ = [
    "TaskProviderProtocol",
    "ContentProviderProtocol",
    "UserProviderProtocol",
    "TaskInfo",
    "ContentInfo",
    "UserInfo",
    "TaskAdapter",
    "ContentAdapter",
    "UserAdapter",
    "InterModuleFacade",
    "get_inter_module_facade",
    "TaskRepositoryProvider",
    "ContentRepositoryProvider",
    "setup_inter_module_adapters",
]
