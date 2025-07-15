"""
Auth response DTOs for API endpoints.
Using Pydantic models for serialization and type safety.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.shared.types import BaseResponse
from app.shared.models import UserRole
from app.core.logging import get_logger

logger = get_logger(__name__)


class UserResponse(BaseResponse):
    """Response model for user information."""
    
    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    username: Optional[str] = Field(None, description="Username")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    full_name: Optional[str] = Field(None, description="Full name")
    display_name: str = Field(..., description="Display name")
    role: UserRole = Field(..., description="User role")
    is_active: bool = Field(..., description="Is user active")
    is_verified: bool = Field(..., description="Is user verified")
    total_tasks_solved: int = Field(..., description="Total tasks solved")
    last_activity_date: Optional[datetime] = Field(None, description="Last activity date")
    created_at: datetime = Field(..., description="Account creation date")
    
    @classmethod
    def from_user(cls, user) -> 'UserResponse':
        """Create response from User model."""
        return cls(
            id=user.id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            display_name=user.display_name,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            total_tasks_solved=user.totalTasksSolved,
            last_activity_date=user.lastActivityDate,
            created_at=user.created_at
        )
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "full_name": "John Doe",
                "display_name": "johndoe",
                "role": "USER",
                "is_active": True,
                "is_verified": True,
                "total_tasks_solved": 15,
                "last_activity_date": "2024-01-15T10:30:00Z",
                "created_at": "2024-01-01T08:00:00Z"
            }
        }


class TokenResponse(BaseResponse):
    """Response model for authentication tokens."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "Bearer",
                "expires_in": 3600
            }
        }


class LoginResponse(BaseResponse):
    """Response model for successful login."""
    
    user: UserResponse = Field(..., description="User information")
    tokens: TokenResponse = Field(..., description="Authentication tokens")
    message: str = Field(default="Login successful", description="Success message")
    
    class Config:
        schema_extra = {
            "example": {
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "username": "johndoe",
                    "display_name": "johndoe",
                    "role": "USER",
                    "is_active": True
                },
                "tokens": {
                    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    "token_type": "Bearer",
                    "expires_in": 3600
                },
                "message": "Login successful"
            }
        }


class RegisterResponse(BaseResponse):
    """Response model for successful registration."""
    
    user: UserResponse = Field(..., description="Created user information")
    tokens: Optional[TokenResponse] = Field(None, description="Authentication tokens (if auto-login)")
    message: str = Field(default="Registration successful", description="Success message")
    requires_verification: bool = Field(default=False, description="Whether email verification is required")
    
    class Config:
        schema_extra = {
            "example": {
                "user": {
                    "id": 2,
                    "email": "newuser@example.com",
                    "username": "newuser123",
                    "display_name": "newuser123",
                    "role": "USER",
                    "is_active": True,
                    "is_verified": False
                },
                "tokens": None,
                "message": "Registration successful. Please verify your email.",
                "requires_verification": True
            }
        }


class RefreshTokenResponse(BaseResponse):
    """Response model for token refresh."""
    
    access_token: str = Field(..., description="New JWT access token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "Bearer",
                "expires_in": 3600
            }
        }


class AuthStatusResponse(BaseResponse):
    """Response model for authentication status check."""
    
    is_authenticated: bool = Field(..., description="Is user authenticated")
    user: Optional[UserResponse] = Field(None, description="User information if authenticated")
    permissions: list[str] = Field(default_factory=list, description="User permissions")
    
    class Config:
        schema_extra = {
            "example": {
                "is_authenticated": True,
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "role": "USER"
                },
                "permissions": ["read_content", "solve_tasks", "view_progress"]
            }
        }


class LogoutResponse(BaseResponse):
    """Response model for logout."""
    
    message: str = Field(default="Logout successful", description="Success message")
    logged_out_devices: int = Field(default=1, description="Number of devices logged out")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Logout successful",
                "logged_out_devices": 1
            }
        }


class PasswordResetResponse(BaseResponse):
    """Response model for password reset initiation."""
    
    message: str = Field(default="Password reset email sent", description="Success message")
    email: str = Field(..., description="Email address where reset link was sent")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "If the email exists, a password reset link has been sent.",
                "email": "user@example.com"
            }
        }


class PasswordResetConfirmResponse(BaseResponse):
    """Response model for password reset confirmation."""
    
    message: str = Field(default="Password reset successful", description="Success message")
    user: UserResponse = Field(..., description="User information")
    tokens: Optional[TokenResponse] = Field(None, description="New tokens (if auto-login)")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Password reset successful",
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "role": "USER"
                },
                "tokens": None
            }
        }


class ChangePasswordResponse(BaseResponse):
    """Response model for password change."""
    
    message: str = Field(default="Password changed successfully", description="Success message")
    user: UserResponse = Field(..., description="User information")
    logout_other_sessions: bool = Field(default=True, description="Whether other sessions were logged out")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Password changed successfully",
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "role": "USER"
                },
                "logout_other_sessions": True
            }
        }


class UpdateProfileResponse(BaseResponse):
    """Response model for profile update."""
    
    message: str = Field(default="Profile updated successfully", description="Success message")
    user: UserResponse = Field(..., description="Updated user information")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Profile updated successfully",
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "username": "updated_username",
                    "first_name": "John",
                    "last_name": "Doe",
                    "role": "USER"
                }
            }
        }


class AuthErrorResponse(BaseResponse):
    """Response model for authentication errors."""
    
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "INVALID_CREDENTIALS",
                "message": "Invalid email or password",
                "details": {
                    "field": "email",
                    "code": "invalid_credentials"
                }
            }
        } 


