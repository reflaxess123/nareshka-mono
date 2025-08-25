"""Session management для совместимости с новой архитектурой"""

from app.shared.database.base import (
    Base,
    BaseModel,
    async_transactional,
    db_manager,
    get_db_session,
    get_db_transaction,
    transactional,
)
from app.shared.database.repository import BaseRepository

engine = db_manager.engine
SessionLocal = db_manager.SessionLocal
get_db = get_db_session

__all__ = [
    "engine",
    "SessionLocal",
    "get_db",
    "get_db_session",
    "get_db_transaction",
    "transactional",
    "async_transactional",
    "BaseRepository",
    "BaseModel",
    "Base",
    "db_manager",
]
