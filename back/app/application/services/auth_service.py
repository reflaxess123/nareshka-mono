"""Сервис авторизации"""

from datetime import datetime, timedelta
from typing import Optional, Union
import uuid

import redis
from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from ...config import new_settings
from ...domain.entities.user import User
from ...domain.entities.enums import UserRole
from ...domain.repositories.user_repository import UserRepository
from ..dto.auth_dto import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse, UserResponse, TokenData


class AuthService:
    """Сервис авторизации"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.redis_client = redis.from_url(new_settings.redis.url, decode_responses=True)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Хеширование пароля"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Создание JWT токена"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=new_settings.auth.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, new_settings.auth.secret_key, algorithm=new_settings.auth.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> TokenData:
        """Проверка JWT токена"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, new_settings.auth.secret_key, algorithms=[new_settings.auth.algorithm])
            email: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            if email is None:
                raise credentials_exception
            return TokenData(email=email, user_id=user_id)
        except JWTError:
            raise credentials_exception
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Аутентификация пользователя"""
        user = await self.user_repository.get_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.password):
            return None
        return user
    
    async def login(self, login_request: LoginRequest) -> LoginResponse:
        """Авторизация пользователя"""
        user = await self.authenticate_user(login_request.email, login_request.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Создаем сессию вместо JWT токена
        session_id = str(uuid.uuid4())
        self.create_session(user.id, session_id)
        
        return LoginResponse(
            access_token="session_based",  # Совместимость с DTO
            token_type="session",
            user=UserResponse.from_orm(user),
            session_id=session_id  # Добавляем session_id для установки cookie
        )
    
    async def register(self, register_request: RegisterRequest) -> RegisterResponse:
        """Регистрация пользователя"""
        if await self.user_repository.email_exists(register_request.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        hashed_password = self.get_password_hash(register_request.password)
        
        new_user = User(
            id=None,  # Auto-increment
            email=register_request.email,
            password=hashed_password,
            role=UserRole.USER,
            createdAt=datetime.utcnow(),
            updatedAt=datetime.utcnow(),
            totalTasksSolved=0,
            lastActivityDate=None
        )
        
        created_user = await self.user_repository.create(new_user)
        
        return RegisterResponse(
            user=UserResponse.from_orm(created_user),
            message="User registered successfully"
        )
    
    def create_session(self, user_id: int, session_id: str) -> None:
        """Создание сессии в Redis"""
        try:
            session_key = f"session:{session_id}"
            self.redis_client.setex(session_key, timedelta(days=new_settings.auth.session_expire_days), str(user_id))
        except Exception as e:
            print(f"Redis error in create_session: {e}")
            # Graceful degradation - сессия не создастся, но приложение не упадет
    
    def get_session_user_id(self, session_id: str) -> Optional[int]:
        """Получение ID пользователя из сессии"""
        try:
            session_key = f"session:{session_id}"
            user_id = self.redis_client.get(session_key)
            return int(user_id) if user_id else None
        except Exception as e:
            print(f"Redis error in get_session_user_id: {e}")
            return None  # Graceful degradation
    
    def delete_session(self, session_id: str) -> None:
        """Удаление сессии"""
        try:
            session_key = f"session:{session_id}"
            self.redis_client.delete(session_key)
        except Exception as e:
            print(f"Redis error in delete_session: {e}")
            # Graceful degradation - сессия не удалится, но приложение не упадет
    
    async def get_user_by_token(self, token: str) -> User:
        """Получение пользователя по токену"""
        token_data = self.verify_token(token)
        user = await self.user_repository.get_by_email(token_data.email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user
    
    async def get_user_by_session(self, request) -> User:
        """Получение пользователя по сессии"""
        session_id = request.cookies.get("session_id")
        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        user_id = self.get_session_user_id(session_id)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired"
            )
        
        user = await self.user_repository.get_by_id(str(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user 