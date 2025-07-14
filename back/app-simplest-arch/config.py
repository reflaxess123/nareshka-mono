from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Определяем базовую директорию проекта (где находится папка back)
# Это делает путь к .env файлу независимым от точки запуска
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = BASE_DIR / "back/.env"


# Проверяем, существует ли файл, чтобы избежать ошибок
if not ENV_FILE_PATH.is_file():
    print(f"DEBUG: .env file NOT found at {ENV_FILE_PATH}")
    # Можно просто проигнорировать или вывести предупреждение,
    # если переменные окружения могут быть заданы другим способом
    # В данном случае мы ожидаем, что они могут быть в среде, поэтому просто продолжаем
    pass
else:
    print(f"DEBUG: .env file found at {ENV_FILE_PATH}")

# Константы для валидации
MAX_EMAIL_LENGTH = 255
MAX_PASSWORD_LENGTH = 255
MIN_PASSWORD_LENGTH = 8
SESSION_EXPIRE_HOURS = 24


class Settings(BaseSettings):
    # База данных
    database_url: str = Field(default="", description="Database URL")

    # Redis
    redis_url: str = Field(default="", description="Redis URL")

    # JWT и безопасность
    secret_key: str = Field(default="", description="Secret key for JWT")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    session_cookie_domain: str = Field(default="localhost", alias="SESSION_COOKIE_DOMAIN")

    # Сервер
    port: int = 4000
    host: str = "0.0.0.0"
    debug: bool = True
    proxy_headers: bool = Field(default=False, alias="PROXY_HEADERS")

    # WebDAV
    webdav_url: str = ""
    webdav_username: str = ""
    webdav_password: str = ""

    # CORS (как строка, разделенная запятыми)
    allowed_origins_str: str = Field(
        default="https://nareshka.site,https://v2.nareshka.site,http://localhost:5173",
        alias="ALLOWED_ORIGINS"
    )

    # OpenAI / ProxyAPI
    proxyapi_key: str = Field(default="", description="ProxyAPI key for OpenAI")

    # Устанавливаем переменную окружения чтобы ai_test_generator мог её использовать
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        import os
        if self.proxyapi_key:
            os.environ["PROXYAPI_KEY"] = self.proxyapi_key

    @property
    def allowed_origins(self) -> List[str]:
        """Парсинг allowed_origins из строки"""
        if not self.allowed_origins_str:
            return ["*"]  # Разрешить все, если не указано

        # Разделяем по запятым и очищаем от пробелов
        origins = [origin.strip() for origin in self.allowed_origins_str.split(",")]
        return [origin for origin in origins if origin]  # Убираем пустые строки

    # Конфигурация модели для Pydantic V2
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE_PATH) if ENV_FILE_PATH.is_file() else None,
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()
print(f"DEBUG: Database URL loaded: {settings.database_url}")
print(f"DEBUG: Redis URL loaded: {settings.redis_url}")
print(f"DEBUG: CORS origins loaded: {settings.allowed_origins}")
print(f"DEBUG: ProxyAPI key loaded: {'*' * (len(settings.proxyapi_key) - 8) + settings.proxyapi_key[-8:] if settings.proxyapi_key else 'NOT SET'}")
