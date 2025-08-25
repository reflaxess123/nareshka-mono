"""Database infrastructure."""

# Import real exceptions instead of stubs
from app.shared.exceptions.base import (
    DatabaseException,
    ResourceConflictException,
    ResourceNotFoundException,
)

from .base import async_transactional, db_manager, transactional
from .connection import Base, SessionLocal, engine, get_db
from .models import AuditMixin, BaseModel, SoftDeleteMixin
from .repository import BaseRepository, ReadOnlyRepository
from .session import get_db_session, get_db_transaction


# Real implementations instead of stubs
def get_database_manager():
    """Get the global database manager"""
    return db_manager


def check_database_health():
    """Check database connection health"""
    return {
        "status": "ok" if db_manager.health_check() else "error",
        "database": "connected" if db_manager.health_check() else "disconnected"
    }


# Alias for compatibility
get_session = get_db
