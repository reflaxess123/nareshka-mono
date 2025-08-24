"""Core Settings - Типизированная система настроек"""

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Главный класс настроек"""

    # App settings
    app_name: str = Field(default="Nareshka", description="Название приложения")
    app_version: str = Field(default="2.0.0", description="Версия приложения")
    app_description: str = Field(
        default="Nareshka - платформа для изучения программирования",
        description="Описание",
    )
    app_environment: str = Field(
        default="development", description="Окружение: development, staging, production"
    )

    # Database settings
    database_url: str = Field(..., description="URL подключения к PostgreSQL")
    database_echo: bool = Field(default=False, description="Логирование SQL запросов")
    database_pool_size: int = Field(default=20, description="Размер connection pool")
    database_max_overflow: int = Field(
        default=30, description="Максимальное переполнение pool"
    )

    # Redis settings
    redis_url: str = Field(..., description="URL подключения к Redis")
    redis_max_connections: int = Field(
        default=100, description="Максимальное количество соединений"
    )

    # Auth settings
    secret_key: str = Field(..., description="Секретный ключ для JWT")
    algorithm: str = Field(default="HS256", description="Алгоритм шифрования JWT")
    access_token_expire_minutes: int = Field(
        default=1440, description="Время жизни access токена в минутах"
    )
    refresh_token_expire_days: int = Field(
        default=30, description="Время жизни refresh токена в днях"
    )

    # Server settings
    host: str = Field(default="0.0.0.0", description="Host для запуска сервера")
    port: int = Field(default=8000, description="Port для запуска сервера")
    debug: bool = Field(default=False, description="Режим отладки")
    allowed_origins: str = Field(default="*", description="Разрешенные CORS origins")

    # Logging settings
    log_level: str = Field(default="INFO", description="Уровень логирования")
    log_format: str = Field(default="json", description="Формат логов: json или text")

    # Additional settings
    proxyapi_key: str = Field(default="", description="Ключ для Proxy API")

    # Additional fields from .env
    uvicorn_log_level: str = Field(
        default="info", description="Уровень логирования Uvicorn"
    )
    watchfiles_log_level: str = Field(
        default="warning", description="Уровень логирования Watchfiles"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env

    @validator("secret_key")
    def validate_secret_key(cls, v):
        if len(v) < 16:
            raise ValueError("Secret key должен быть не менее 16 символов")
        return v

    @validator("app_environment")
    def validate_environment(cls, v):
        if v not in ["development", "staging", "production"]:
            raise ValueError(
                "Environment должен быть: development, staging, production"
            )
        return v

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validate_settings()

    def _validate_settings(self):
        """Дополнительная валидация настроек"""
        if self.app_environment == "production":
            if not self.secret_key or self.secret_key == "changeme":
                raise ValueError("В production нужен надежный SECRET_KEY")
            if self.debug:
                raise ValueError("В production нельзя включать DEBUG")

    @property
    def is_development(self) -> bool:
        """Проверка на режим разработки"""
        return self.app_environment == "development"


settings = Settings()
