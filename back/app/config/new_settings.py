"""Типизированная конфигурация для новой архитектуры"""

import os
from enum import Enum
from pathlib import Path
from typing import List

from pydantic import BaseModel

# Загружаем .env файл вручную - исправляю путь
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"

# Читаем .env файл
if ENV_FILE_PATH.exists():
    with open(ENV_FILE_PATH, encoding="utf-8") as f:
        for original_line in f:
            line = original_line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key] = value


class Environment(str, Enum):
    """Окружение приложения"""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class DatabaseSettings(BaseModel):
    """Настройки базы данных"""

    url: str
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20


class RedisSettings(BaseModel):
    """Настройки Redis"""

    url: str
    decode_responses: bool = True


class AuthSettings(BaseModel):
    """Настройки авторизации"""

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    session_expire_days: int = 1


class ServerSettings(BaseModel):
    """Настройки сервера"""

    host: str = "0.0.0.0"
    port: int = 4000
    debug: bool = False
    cors_origins: List[str] = []


class CodeExecutionSettings(BaseModel):
    """Настройки выполнения кода"""

    timeout_seconds: int = 10
    memory_limit_mb: int = 128
    max_file_size_mb: int = 1
    temp_dir: str = "/tmp/code_execution"


class ExternalAPISettings(BaseModel):
    """Настройки внешних API"""

    proxy_api_key: str


class ApplicationSettings(BaseModel):
    """Основные настройки приложения"""

    environment: Environment = Environment.DEVELOPMENT
    app_name: str = "Nareshka API"
    version: str = "2.0.0"
    description: str = "Nareshka Learning Platform API"
    log_level: str = "INFO"

    # Подразделы конфигурации
    database: DatabaseSettings
    redis: RedisSettings
    auth: AuthSettings
    server: ServerSettings
    code_execution: CodeExecutionSettings
    external_api: ExternalAPISettings


class LegacySettingsAdapter:
    """Адаптер для совместимости со старыми настройками"""

    def __init__(self, new_settings: ApplicationSettings):
        self._new_settings = new_settings

    # Адаптируем свойства для старого кода
    @property
    def redis_url(self) -> str:
        return self._new_settings.redis.url

    @property
    def access_token_expire_minutes(self) -> int:
        return self._new_settings.auth.access_token_expire_minutes

    @property
    def secret_key(self) -> str:
        return self._new_settings.auth.secret_key

    @property
    def algorithm(self) -> str:
        return self._new_settings.auth.algorithm

    @property
    def database_url(self) -> str:
        return self._new_settings.database.url

    @property
    def host(self) -> str:
        return self._new_settings.server.host

    @property
    def port(self) -> int:
        return self._new_settings.server.port

    @property
    def debug(self) -> bool:
        return self._new_settings.server.debug

    @property
    def allowed_origins(self) -> List[str]:
        return self._new_settings.server.cors_origins

    @property
    def proxyapi_key(self) -> str:
        return self._new_settings.external_api.proxy_api_key

    @property
    def proxy_headers(self) -> bool:
        return False  # Default value for proxy headers

    @property
    def session_cookie_domain(self) -> str:
        return "localhost"  # Default value

    @property
    def webdav_url(self) -> str:
        return os.getenv("WEBDAV_URL", "")

    @property
    def webdav_username(self) -> str:
        return os.getenv("WEBDAV_USERNAME", "")

    @property
    def webdav_password(self) -> str:
        return os.getenv("WEBDAV_PASSWORD", "")

    @property
    def log_level(self) -> str:
        return self._new_settings.log_level


# Создаем настройки на основе переменных окружения
def create_new_settings() -> ApplicationSettings:
    """Создает новые настройки на основе переменных окружения"""
    # Парсим CORS origins
    cors_origins_str = os.getenv("ALLOWED_ORIGINS", "")
    cors_origins = []
    if cors_origins_str:
        cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]

    return ApplicationSettings(
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        database=DatabaseSettings(
            url=os.getenv("DATABASE_URL", ""),
            echo=os.getenv("DEBUG", "False").lower() == "true",
            pool_size=10,
            max_overflow=20,
        ),
        redis=RedisSettings(url=os.getenv("REDIS_URL", ""), decode_responses=True),
        auth=AuthSettings(
            secret_key=os.getenv("SECRET_KEY", ""),
            algorithm=os.getenv("ALGORITHM", "HS256"),
            access_token_expire_minutes=int(
                os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
            ),
            session_expire_days=1,
        ),
        server=ServerSettings(
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "4000")),
            debug=os.getenv("DEBUG", "False").lower() == "true",
            cors_origins=cors_origins,
        ),
        code_execution=CodeExecutionSettings(
            timeout_seconds=10,
            memory_limit_mb=128,
            max_file_size_mb=1,
            temp_dir="/tmp/code_execution",
        ),
        external_api=ExternalAPISettings(proxy_api_key=os.getenv("PROXYAPI_KEY", "")),
    )


# Глобальная конфигурация
new_settings = create_new_settings()
legacy_settings = LegacySettingsAdapter(new_settings)


def get_settings() -> LegacySettingsAdapter:
    """Возвращает настройки приложения для обратной совместимости"""
    return legacy_settings
