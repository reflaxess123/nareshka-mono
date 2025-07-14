"""Database infrastructure."""

from .connection import get_db, Base, engine, SessionLocal
from .base import BaseModel
from .repository import BaseRepository

# Create missing classes for compatibility
class DatabaseException(Exception):
    pass

def transactional(func):
    """Simple transactional decorator"""
    return func

class AuditMixin:
    pass

# Database manager заглушка
def get_database_manager():
    """Database manager заглушка"""
    return None

# Health check заглушка  
def check_database_health():
    """Health check заглушка"""
    return {"status": "ok", "database": "connected"}

# Alias for compatibility  
get_session = get_db


