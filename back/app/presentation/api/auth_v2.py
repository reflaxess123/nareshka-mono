"""API для авторизации (новая архитектура)"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from ...application.dto.auth_dto import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse, UserResponse
from ...application.services.auth_service import AuthService
from ...domain.repositories.unit_of_work import UnitOfWork
from ...shared.dependencies import get_unit_of_work

router = APIRouter(prefix="/auth", tags=["auth"])


async def get_auth_service(uow: UnitOfWork = Depends(get_unit_of_work)) -> AuthService:
    """Получение сервиса авторизации"""
    async with uow:
        return AuthService(uow.users)


@router.post("/login", response_model=LoginResponse)
async def login(
    login_request: LoginRequest,
    response: Response,
    uow: UnitOfWork = Depends(get_unit_of_work)
):
    """Авторизация пользователя"""
    async with uow:
        auth_service = AuthService(uow.users)
        login_response = await auth_service.login(login_request)
        
        # Устанавливаем session cookie
        if login_response.session_id:
            response.set_cookie(
                key="session_id",
                value=login_response.session_id,
                httponly=True,
                secure=False,  # True в продакшене для HTTPS
                samesite="lax",
                max_age=24 * 60 * 60  # 24 часа
            )
        
        return login_response


@router.post("/register", response_model=RegisterResponse)
async def register(
    register_request: RegisterRequest,
    uow: UnitOfWork = Depends(get_unit_of_work)
):
    """Регистрация пользователя"""
    async with uow:
        auth_service = AuthService(uow.users)
        return await auth_service.register(register_request)


@router.get("/me", response_model=UserResponse)
async def get_me(
    request: Request,
    uow: UnitOfWork = Depends(get_unit_of_work)
):
    """Получение данных текущего пользователя"""
    async with uow:
        auth_service = AuthService(uow.users)
        user = await auth_service.get_user_by_session(request)
        return UserResponse.from_orm(user)


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    uow: UnitOfWork = Depends(get_unit_of_work)
):
    """Выход из системы"""
    session_id = request.cookies.get("session_id")
    if session_id:
        async with uow:
            auth_service = AuthService(uow.users)
            auth_service.delete_session(session_id)
    
    # Удаляем cookie
    response.delete_cookie("session_id")
    return {"message": "Logged out successfully"} 