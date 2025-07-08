"""API для аутентификации v2"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from ...application.services.auth_service import AuthService
from ...application.dto.auth_dto import (
    LoginRequest, 
    LoginResponse, 
    RegisterRequest, 
    RegisterResponse,
    LogoutResponse
)
from ...shared.dependencies import get_auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Вход пользователя"""
    
    login_response = await auth_service.login(request)
    
    # Устанавливаем cookie с session_id
    if hasattr(login_response, 'session_id'):
        response.set_cookie(
            key="session_id", 
            value=login_response.session_id,
            httponly=True,
            secure=False,  # В dev режиме
            samesite="lax"
        )
    
    return login_response


@router.post("/register", response_model=RegisterResponse)
async def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Регистрация пользователя"""
    
    return await auth_service.register(request)


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Выход пользователя"""
    
    session_id = request.cookies.get("session_id")
    if session_id:
        auth_service.delete_session(session_id)
    
    # Удаляем cookie
    response.delete_cookie(key="session_id")
    
    return LogoutResponse(message="Successfully logged out")


@router.get("/me")
async def get_current_user_info(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Получение информации о текущем пользователе"""
    
    user = await auth_service.get_user_by_session(request)
    
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "totalTasksSolved": user.totalTasksSolved,
        "createdAt": user.createdAt,
        "lastActivityDate": user.lastActivityDate
    } 