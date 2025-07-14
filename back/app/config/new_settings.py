""""8?878@>20==0O :>=D83C@0F8O 4;O =>2>9 0@E8B5:BC@K"""

import os
from enum import Enum
from pathlib import Path
from typing import List

from pydantic import BaseModel

# 03@C605< .env D09; 2@CG=CN - 8A?@02;ON ?CBL
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"

# '8B05< .env D09;
if ENV_FILE_PATH.exists():
    with open(ENV_FILE_PATH, encoding="utf-8") as f:
        for original_line in f:
            line = original_line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key] = value


class Environment(str, Enum):
    """:@C65=85 ?@8;>65=8O"""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class DatabaseSettings(BaseModel):
    """0AB@>9:8 107K 40==KE"""

    url: str
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20


class RedisSettings(BaseModel):
    """0AB@>9:8 Redis"""

    url: str
    decode_responses: bool = True


class AuthSettings(BaseModel):
    """0AB@>9:8 02B>@870F88"""

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    session_expire_days: int = 1


class ServerSettings(BaseModel):
    """0AB@>9:8 A5@25@0"""

    host: str = "0.0.0.0"
    port: int = 4000
    debug: bool = False
    cors_origins: List[str] = []


class CodeExecutionSettings(BaseModel):
    """0AB@>9:8 2K?>;=5=8O :>40"""

    timeout_seconds: int = 10
    memory_limit_mb: int = 128
    max_file_size_mb: int = 1
    temp_dir: str = "/tmp/code_execution"


class ExternalAPISettings(BaseModel):
    """0AB@>9:8 2=5H=8E API"""

    proxy_api_key: str


class ApplicationSettings(BaseModel):
    """A=>2=K5 =0AB@>9:8 ?@8;>65=8O"""

    environment: Environment = Environment.DEVELOPMENT
    app_name: str = "Nareshka API"
    version: str = "2.0.0"
    description: str = "Nareshka Learning Platform API"

    # >4@0745;K :>=D83C@0F88
    database: DatabaseSettings
    redis: RedisSettings
    auth: AuthSettings
    server: ServerSettings
    code_execution: CodeExecutionSettings
    external_api: ExternalAPISettings


class LegacySettingsAdapter:
    """40?B5@ 4;O A>2<5AB8<>AB8 A> AB0@K<8 =0AB@>9:0<8"""

    def __init__(self, new_settings: ApplicationSettings):
        self._new_settings = new_settings

    # 40?B8@C5< A2>9AB20 4;O AB0@>3> :>40
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


# !>7405< =0AB@>9:8 =0 >A=>25 ?5@5<5==KE >:@C65=8O
def create_new_settings() -> ApplicationSettings:
    """!>7405B =>2K5 =0AB@>9:8 =0 >A=>25 ?5@5<5==KE >:@C65=8O"""
    # 0@A8< CORS origins
    cors_origins_str = os.getenv("ALLOWED_ORIGINS", "")
    cors_origins = []
    if cors_origins_str:
        cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]

    return ApplicationSettings(
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


# ;>10;L=0O :>=D83C@0F8O
new_settings = create_new_settings()
legacy_settings = LegacySettingsAdapter(new_settings)


def get_settings() -> LegacySettingsAdapter:
    """>72@0I05B =0AB@>9:8 ?@8;>65=8O 4;O >1@0B=>9 A>2<5AB8<>AB8"""
    return legacy_settings