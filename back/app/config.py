from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Константы для валидации
MAX_EMAIL_LENGTH = 255
MAX_PASSWORD_LENGTH = 255
MIN_PASSWORD_LENGTH = 8
SESSION_EXPIRE_HOURS = 24


class Settings(BaseSettings):
    # База данных
    database_url: str
    
    # Redis
    redis_url: str
    
    # JWT и безопасность
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    # Сервер
    port: int = 4000
    host: str = "0.0.0.0"
    debug: bool = True
    
    # WebDAV
    webdav_url: str = ""
    webdav_username: str = ""
    webdav_password: str = ""
    
    # CORS (как строка, разделенная запятыми)
    allowed_origins_str: str = Field(
        default="https://nareshka.site,https://v2.nareshka.site,http://localhost:5173",
        alias="ALLOWED_ORIGINS"
    )
    
    @property
    def allowed_origins(self) -> List[str]:
        """Парсинг allowed_origins из строки"""
        if not self.allowed_origins_str:
            return ["*"]  # Разрешить все, если не указано
        
        # Разделяем по запятым и очищаем от пробелов
        origins = [origin.strip() for origin in self.allowed_origins_str.split(',')]
        return [origin for origin in origins if origin]  # Убираем пустые строки
    
    # Конфигурация модели для Pydantic V2
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # Игнорируем дополнительные поля от Coolify
    )


settings = Settings() 