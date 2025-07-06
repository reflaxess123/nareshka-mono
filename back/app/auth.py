from datetime import datetime, timedelta
from typing import Optional, Union

import redis
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .config.new_settings import legacy_settings
from .database import get_db
from .models import User

# Настройка криптографии
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Redis клиент для сессий
redis_client = redis.from_url(legacy_settings.redis_url, decode_responses=True)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=legacy_settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, legacy_settings.secret_key, algorithm=legacy_settings.algorithm)
    return encoded_jwt


def verify_token(token: str, credentials_exception):
    """Проверка JWT токена"""
    try:
        payload = jwt.decode(token, legacy_settings.secret_key, algorithms=[legacy_settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    except JWTError:
        raise credentials_exception


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Получение пользователя по email"""
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str) -> Union[User, bool]:
    """Аутентификация пользователя"""
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Получение текущего пользователя по токену"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    email = verify_token(token, credentials_exception)
    user = get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Получение активного пользователя"""
    return current_user


def require_admin(request: Request, db: Session = Depends(get_db)) -> User:
    """
    Проверка прав администратора
    Выбрасывает HTTPException если пользователь не админ
    """
    user = get_current_user_from_session_required(request, db)
    if user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions. Admin access required."
        )
    return user


# Альтернативная система на основе сессий (как в оригинале)
def create_session(user_id: int, session_id: str) -> None:
    """Создание сессии в Redis"""
    try:
        session_key = f"session:{session_id}"
        redis_client.setex(session_key, timedelta(days=1), str(user_id))
    except Exception as e:
        print(f"Redis error in create_session: {e}")
        # Graceful degradation - сессия не создастся, но приложение не упадет


def get_session_user_id(session_id: str) -> Optional[int]:
    """Получение ID пользователя из сессии"""
    try:
        session_key = f"session:{session_id}"
        user_id = redis_client.get(session_key)
        return int(user_id) if user_id else None
    except Exception as e:
        print(f"Redis error in get_session_user_id: {e}")
        return None  # Graceful degradation


def delete_session(session_id: str) -> None:
    """Удаление сессии"""
    try:
        session_key = f"session:{session_id}"
        redis_client.delete(session_key)
    except Exception as e:
        print(f"Redis error in delete_session: {e}")
        # Graceful degradation - сессия не удалится, но приложение не упадет


def get_current_user_from_session(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Получение пользователя из сессии (для совместимости)"""
    session_id = request.cookies.get("session_id")
    if not session_id:
        return None

    user_id = get_session_user_id(session_id)
    if not user_id:
        return None

    return db.query(User).filter(User.id == user_id).first()


def get_current_user_from_session_required(request: Request, db: Session) -> User:
    """
    Получение текущего пользователя из сессии (обязательно)
    Выбрасывает HTTPException если пользователь не авторизован
    """
    user = get_current_user_from_session(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user
