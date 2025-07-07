"""Сервисы приложения"""

from .admin_service import AdminService
from .auth_service import AuthService
from .code_editor_service import CodeEditorService
from .content_service import ContentService
from .mindmap_service import MindMapService
from .progress_service import ProgressService
from .stats_service import StatsService
from .task_service import TaskService
from .theory_service import TheoryService
from .code_executor_service import CodeExecutorService
from .ai_test_generator_service import AITestGeneratorService

__all__ = [
    'AdminService',
    'AuthService',
    'CodeEditorService',
    'ContentService',
    'MindMapService',
    'ProgressService',
    'StatsService',
    'TaskService',
    'TheoryService',
    'CodeExecutorService',
    'AITestGeneratorService'
] 