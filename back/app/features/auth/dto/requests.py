"""
Auth request DTOs for API endpoints.
Using Pydantic models for validation and serialization.
"""

from typing import Optional
from pydantic import BaseModel, Field, validator

from app.shared.utils import validate_email_format, validate_password_strength
from pydantic import EmailStr
from app.shared.types import BaseCreateRequest, BaseUpdateRequest
from app.shared.models import UserRole
from app.core.logging import get_logger

logger = get_logger(__name__)


class LoginRequest(BaseModel):
    """Request model for user login."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")
    remember_me: bool = Field(default=False, description="Keep user logged in")
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        if not validate_email_format(v):
            raise ValueError('Invalid email format')
        return v.lower().strip()
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "MySecurePassword123",
                "remember_me": False
            }
        }


class RegisterRequest(BaseCreateRequest):
    """Request model for user registration."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    password_confirm: str = Field(..., description="Password confirmation")
    username: Optional[str] = Field(None, min_length=3, max_length=20, description="Username (optional)")
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        if not validate_email_format(v):
            raise ValueError('Invalid email format')
        return v.lower().strip()
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        result = validate_password_strength(v)
        if not result.is_valid:
            raise ValueError('; '.join(result.errors))
        return v
    
    @validator('password_confirm')
    def validate_password_match(cls, v, values):
        """Validate password confirmation matches."""
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format."""
        if v is None:
            return v
        
        v = v.strip()
        if not v.replace('_', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "email": "newuser@example.com",
                "password": "MySecurePassword123",
                "password_confirm": "MySecurePassword123",
                "username": "newuser123",
                "first_name": "John",
                "last_name": "Doe"
            }
        }


class PasswordResetRequest(BaseModel):
    """Request model for password reset initiation."""
    
    email: EmailStr = Field(..., description="User email address")
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        if not validate_email_format(v):
            raise ValueError('Invalid email format')
        return v.lower().strip()
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


class PasswordResetConfirmRequest(BaseModel):
    """Request model for password reset confirmation."""
    
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    new_password_confirm: str = Field(..., description="New password confirmation")
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength."""
        result = validate_password_strength(v)
        if not result.is_valid:
            raise ValueError('; '.join(result.errors))
        return v
    
    @validator('new_password_confirm')
    def validate_password_match(cls, v, values):
        """Validate password confirmation matches."""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "token": "abc123def456",
                "new_password": "MyNewSecurePassword123",
                "new_password_confirm": "MyNewSecurePassword123"
            }
        }


class ChangePasswordRequest(BaseModel):
    """Request model for password change (when authenticated)."""
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    new_password_confirm: str = Field(..., description="New password confirmation")
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength."""
        result = validate_password_strength(v)
        if not result.is_valid:
            raise ValueError('; '.join(result.errors))
        return v
    
    @validator('new_password_confirm')
    def validate_password_match(cls, v, values):
        """Validate password confirmation matches."""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "current_password": "MyOldPassword123",
                "new_password": "MyNewSecurePassword123",
                "new_password_confirm": "MyNewSecurePassword123"
            }
        }


class UpdateUserProfileRequest(BaseUpdateRequest):
    """Request model for updating user profile."""
    
    username: Optional[str] = Field(None, min_length=3, max_length=20, description="Username")
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format."""
        if v is None:
            return v
        
        v = v.strip()
        if not v.replace('_', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "username": "updated_username",
                "first_name": "John",
                "last_name": "Doe"
            }
        }


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh."""
    
    refresh_token: str = Field(..., description="Refresh token")
    
    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            }
        }


class LogoutRequest(BaseModel):
    """Request model for logout (optional token invalidation)."""
    
    logout_all_devices: bool = Field(default=False, description="Logout from all devices")
    
    class Config:
        schema_extra = {
            "example": {
                "logout_all_devices": False
            }
        } 


