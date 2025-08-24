"""Admin module custom exceptions"""

from app.shared.exceptions.base import BaseAppException


class AdminException(BaseAppException):
    """Base exception for admin operations"""
    pass


class AdminAccessDeniedException(AdminException):
    """Raised when non-admin user tries to access admin resources"""
    
    def __init__(self, message: str = "Admin access required"):
        super().__init__(message, status_code=403)


class AdminStatsException(AdminException):
    """Raised when admin stats cannot be retrieved"""
    
    def __init__(self, message: str = "Failed to retrieve admin statistics"):
        super().__init__(message, status_code=500)