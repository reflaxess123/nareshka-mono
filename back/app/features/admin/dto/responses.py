"""Admin response DTOs for API endpoints"""

from typing import Optional

from pydantic import Field

from app.shared.types import BaseResponse
from app.features.auth.dto.auth_dto import UserResponse


class UserStatsResponse(BaseResponse):
    """Statistics about users"""
    
    total: int = Field(..., description="Total number of users")
    admins: int = Field(..., description="Number of admin users")
    regular_users: int = Field(..., description="Number of regular users", alias="regularUsers")
    guests: int = Field(..., description="Number of guest users")


class ContentStatsResponse(BaseResponse):
    """Statistics about content"""
    
    total_files: int = Field(..., description="Total number of content files", alias="totalFiles")
    total_blocks: int = Field(..., description="Total number of content blocks", alias="totalBlocks")
    total_theory_cards: int = Field(..., description="Total number of theory cards", alias="totalTheoryCards")


class ProgressStatsResponse(BaseResponse):
    """Statistics about user progress"""
    
    total_content_progress: int = Field(..., description="Total content progress records", alias="totalContentProgress")
    total_theory_progress: int = Field(..., description="Total theory progress records", alias="totalTheoryProgress")


class SystemStatsResponse(BaseResponse):
    """System health and performance statistics"""
    
    uptime_seconds: Optional[int] = Field(None, description="System uptime in seconds", alias="uptimeSeconds")
    memory_usage_mb: Optional[float] = Field(None, description="Memory usage in MB", alias="memoryUsageMB")
    database_connections: Optional[int] = Field(None, description="Active database connections", alias="databaseConnections")


class UsersListResponse(BaseResponse):
    """Response for admin users list"""
    
    items: list[UserResponse] = Field(..., description="List of users")
    pagination: dict = Field(..., description="Pagination info")


class AdminStatsResponse(BaseResponse):
    """Complete admin dashboard statistics"""
    
    users: UserStatsResponse = Field(..., description="User statistics")
    content: ContentStatsResponse = Field(..., description="Content statistics")
    progress: ProgressStatsResponse = Field(..., description="Progress statistics")
    system: Optional[SystemStatsResponse] = Field(None, description="System statistics")
    error: Optional[str] = Field(None, description="Error message if any")