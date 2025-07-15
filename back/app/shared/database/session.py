"""Session management для совместимости с новой архитектурой"""

from app.shared.database.base import (
    db_manager,
    get_db_session,
    get_db_transaction,
    transactional,
    async_transactional,
    BaseRepository,
    BaseModel,
    Base
)

# Экспорт для обратной совместимости
engine = db_manager.engine
SessionLocal = db_manager.SessionLocal
get_db = get_db_session

# Экспорт всех необходимых компонентов
__all__ = [
    'engine',
    'SessionLocal',
    'get_db',
    'get_db_session',
    'get_db_transaction',
    'transactional',
    'async_transactional',
    'BaseRepository',
    'BaseModel',
    'Base',
    'db_manager'
] 


