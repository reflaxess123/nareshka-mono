"""Реализация Unit of Work для SQLAlchemy"""

from sqlalchemy.orm import Session
from ...domain.repositories.unit_of_work import UnitOfWork
from ...domain.repositories.user_repository import UserRepository
from ...domain.repositories.content_repository import ContentRepository
from ...domain.repositories.theory_repository import TheoryRepository
from ...domain.repositories.task_repository import TaskRepository
from ...domain.repositories.progress_repository import ProgressRepository
from ...domain.repositories.code_editor_repository import CodeEditorRepository
from ...domain.repositories.stats_repository import StatsRepository
from ...domain.repositories.mindmap_repository import MindMapRepository
from ...domain.repositories.admin_repository import AdminRepository
from ..repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from ..repositories.sqlalchemy_content_repository import SQLAlchemyContentRepository
from ..repositories.sqlalchemy_theory_repository import SQLAlchemyTheoryRepository
from ..repositories.sqlalchemy_task_repository import SQLAlchemyTaskRepository
from ..repositories.sqlalchemy_progress_repository import SQLAlchemyProgressRepository
from ..repositories.sqlalchemy_code_editor_repository import SQLAlchemyCodeEditorRepository
from ..repositories.sqlalchemy_stats_repository import SQLAlchemyStatsRepository
from ..repositories.sqlalchemy_mindmap_repository import SqlAlchemyMindMapRepository
from ..repositories.sqlalchemy_admin_repository import SQLAlchemyAdminRepository
from .connection import SessionLocal


class SQLAlchemyUnitOfWork(UnitOfWork):
    """Реализация Unit of Work для SQLAlchemy"""
    
    def __init__(self):
        self.session: Session = None
        self.users: UserRepository = None
        self.content: ContentRepository = None
        self.theory: TheoryRepository = None
        self.tasks: TaskRepository = None
        self.progress: ProgressRepository = None
        self.code_editor: CodeEditorRepository = None
        self.stats: StatsRepository = None
        self.mindmap: MindMapRepository = None
        self.admin: AdminRepository = None
    
    async def __aenter__(self):
        """Начало транзакции"""
        self.session = SessionLocal()
        self.users = SQLAlchemyUserRepository(self.session)
        self.content = SQLAlchemyContentRepository(self.session)
        self.theory = SQLAlchemyTheoryRepository(self.session)
        self.tasks = SQLAlchemyTaskRepository(self.session)
        self.progress = SQLAlchemyProgressRepository(self.session)
        self.code_editor = SQLAlchemyCodeEditorRepository(self.session)
        self.stats = SQLAlchemyStatsRepository(self.session)
        self.mindmap = SqlAlchemyMindMapRepository(self.session)
        self.admin = SQLAlchemyAdminRepository(self.session)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Завершение транзакции с rollback при ошибке"""
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        self.session.close()
    
    async def commit(self):
        """Подтверждение транзакции"""
        self.session.commit()
    
    async def rollback(self):
        """Откат транзакции"""
        self.session.rollback() 