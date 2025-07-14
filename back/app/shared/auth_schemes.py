"""Общие схемы аутентификации для приложения"""

from fastapi.security import OAuth2PasswordBearer

# OAuth2 scheme для JWT аутентификации
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v2/auth/login")



