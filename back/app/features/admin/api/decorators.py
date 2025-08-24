"""Admin API decorators"""

from functools import wraps
from fastapi import Depends
from app.shared.dependencies import get_current_admin_session
from app.shared.models.user_models import User
from app.features.admin.exceptions import AdminAccessDeniedException


def require_admin(func):
    """
    Decorator to ensure user has admin access
    Usage:
        @require_admin
        @router.get("/endpoint")
        async def admin_endpoint(current_admin: User = Depends(get_current_admin_session)):
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Find current_admin in kwargs
        current_admin = None
        for key, value in kwargs.items():
            if isinstance(value, User):
                current_admin = value
                break
        
        if not current_admin or current_admin.role != "ADMIN":
            raise AdminAccessDeniedException()
        
        return await func(*args, **kwargs)
    
    return wrapper