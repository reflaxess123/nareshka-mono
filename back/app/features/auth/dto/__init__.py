# Auth DTOs

from .requests import (
    LoginRequest,
    RegisterRequest,
    PasswordResetRequest,
    PasswordResetConfirmRequest,
    ChangePasswordRequest,
    UpdateUserProfileRequest,
    RefreshTokenRequest,
    LogoutRequest
)

from .responses import (
    UserResponse,
    TokenResponse,
    LoginResponse,
    RegisterResponse,
    RefreshTokenResponse,
    AuthStatusResponse,
    LogoutResponse,
    PasswordResetResponse,
    PasswordResetConfirmResponse,
    ChangePasswordResponse,
    UpdateProfileResponse,
    AuthErrorResponse
)

__all__ = [
    # Requests
    "LoginRequest",
    "RegisterRequest",
    "PasswordResetRequest",
    "PasswordResetConfirmRequest",
    "ChangePasswordRequest",
    "UpdateUserProfileRequest",
    "RefreshTokenRequest",
    "LogoutRequest",
    
    # Responses
    "UserResponse",
    "TokenResponse",
    "LoginResponse",
    "RegisterResponse",
    "RefreshTokenResponse",
    "AuthStatusResponse",
    "LogoutResponse",
    "PasswordResetResponse",
    "PasswordResetConfirmResponse",
    "ChangePasswordResponse",
    "UpdateProfileResponse",
    "AuthErrorResponse",
] 



