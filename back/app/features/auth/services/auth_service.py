"""Сервис авторизации"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

import redis
from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.features.auth.dto.auth_dto import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    TokenData,
    UserResponse,
)
from app.config.settings import settings
from app.core.exceptions import GracefulDegradation
from app.core.logging import get_logger
from app.features.auth.repositories.user_repository import UserRepository
from app.shared.models.enums import UserRole
from app.shared.models.user_models import User

logger = get_logger(__name__)


class AuthService:
    """Сервис авторизации"""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.redis_client = redis.from_url(
            "redis://127.0.0.1:6379/0", decode_responses=True
        )

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Хеширование пароля"""
        return self.pwd_context.hash(password)

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Создание JWT токена"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.access_token_expire_minutes
            )

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm,
        )
        return encoded_jwt

    def verify_token(self, token: str) -> TokenData:
        """Проверка JWT токена"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm],
            )
            email: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            if email is None:
                raise credentials_exception
            return TokenData(email=email, user_id=user_id)
        except JWTError as e:
            raise credentials_exception from e

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Аутентификация пользователя"""
        import time
        
        start_db = time.time()
        user = await self.user_repository.get_by_email(email)
        db_time = time.time() - start_db
        logger.info(f"🔍 GET_BY_EMAIL took {db_time:.3f}s")
        
        if not user:
            return None
            
        start_pwd = time.time()
        pwd_valid = self.verify_password(password, user.password)
        pwd_time = time.time() - start_pwd
        logger.info(f"🔍 VERIFY_PASSWORD took {pwd_time:.3f}s")
        
        if not pwd_valid:
            return None
        return user

    async def login(self, login_request: LoginRequest) -> LoginResponse:
        """Авторизация пользователя"""
        import time
        logger.info(f"🔍 LOGIN START for {login_request.email}")
        
        start_time = time.time()
        user = await self.authenticate_user(login_request.email, login_request.password)
        auth_time = time.time() - start_time
        logger.info(f"🔍 AUTHENTICATE_USER took {auth_time:.3f}s")
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        # Создаем сессию вместо JWT токена
        session_id = str(uuid.uuid4())
        
        start_session = time.time()
        self.create_session(user.id, session_id)
        session_time = time.time() - start_session
        logger.info(f"🔍 CREATE_SESSION took {session_time:.3f}s")
        
        start_response = time.time()
        response = LoginResponse(
            access_token="session_based",  # Совместимость с DTO
            token_type="session",
            user=UserResponse.model_validate(user),
            session_id=session_id,  # Добавляем session_id для установки cookie
        )
        response_time = time.time() - start_response
        logger.info(f"🔍 CREATE_RESPONSE took {response_time:.3f}s")
        
        logger.info(f"🔍 LOGIN COMPLETE for {login_request.email}")
        return response

    async def register(self, register_request: RegisterRequest) -> RegisterResponse:
        """Регистрация пользователя"""
        if await self.user_repository.email_exists(register_request.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        hashed_password = self.get_password_hash(register_request.password)

        new_user = User(
            email=register_request.email,
            password=hashed_password,
            role=UserRole.USER,
            totalTasksSolved=0,
            lastActivityDate=None,
        )

        created_user = await self.user_repository.create(new_user)

        return RegisterResponse(
            user=UserResponse.model_validate(created_user),
            message="User registered successfully",
        )

    def create_session(self, user_id: int, session_id: str) -> None:
        """Создание сессии в Redis"""
        try:
            session_key = f"session:{session_id}"
            self.redis_client.setex(
                session_key,
                timedelta(days=settings.refresh_token_expire_days),
                str(user_id),
            )
        except Exception as e:
            GracefulDegradation.handle_redis_error("create_session", e)
            # Graceful degradation - сессия не создастся, но приложение не упадет

    def get_session_user_id(self, session_id: str) -> Optional[int]:
        """Получение ID пользователя из сессии"""
        try:
            session_key = f"session:{session_id}"
            user_id = self.redis_client.get(session_key)
            return int(user_id) if user_id else None
        except Exception as e:
            return GracefulDegradation.handle_redis_error(
                "get_session_user_id", e, None
            )

    def delete_session(self, session_id: str) -> None:
        """Удаление сессии"""
        try:
            session_key = f"session:{session_id}"
            self.redis_client.delete(session_key)
        except Exception as e:
            GracefulDegradation.handle_redis_error("delete_session", e)
            # Graceful degradation - сессия не удалится, но приложение не упадет

    async def get_user_by_token(self, token: str) -> User:
        """Получение пользователя по токену"""
        token_data = self.verify_token(token)
        user = await self.user_repository.get_by_email(token_data.email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )
        return user

    async def get_user_by_session(self, request) -> User:
        """Получение пользователя по сессии"""
        session_id = request.cookies.get("session_id")
        logger.info(f"🔍 DEBUG: get_user_by_session called", extra={
            "has_session_id": session_id is not None,
            "session_id_prefix": session_id[:10] + "..." if session_id else None
        })
        
        if not session_id:
            logger.info(f"🔍 DEBUG: No session_id cookie found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
            )

        user_id = self.get_session_user_id(session_id)
        logger.info(f"🔍 DEBUG: Session lookup result", extra={
            "session_id_prefix": session_id[:10] + "...",
            "user_id": user_id
        })
        
        if not user_id:
            logger.info(f"🔍 DEBUG: Session expired or not found in Redis")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired"
            )

        user = await self.user_repository.get_by_id(user_id)
        if not user:
            logger.info(f"🔍 DEBUG: User not found in database", extra={
                "user_id": user_id
            })
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )
            
        logger.info(f"🔍 DEBUG: User successfully retrieved from session", extra={
            "user_id": user.id,
            "user_email": user.email
        })
        return user 


