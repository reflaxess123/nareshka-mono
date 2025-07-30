#!/usr/bin/env python3
"""FastAPI приложение nareshka"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.config.settings import settings
from app.core.error_handlers import register_exception_handlers
from app.core.logging import get_logger, init_default_logging
from app.shared.di import setup_di_container
from app.features.admin.api.admin_router import router as admin_router
from app.features.auth.api.auth_router import router as auth_router
from app.features.browser_logs.api.browser_logs_router import router as browser_logs_router
from app.features.code_editor.api import router as code_editor_router
from app.features.content.api import router as content_router
from app.features.mindmap.api import router as mindmap_router
from app.features.progress.api import router as progress_router
from app.features.stats.api import router as stats_router
from app.features.task.api import router as task_router
from app.features.theory.api import router as theory_router

# Инициализируем логирование
init_default_logging()
logger = get_logger(__name__)


# Старые роутеры удалены для полного перехода на новую архитектуру


# Событие startup - выполняется один раз при запуске приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация DI Container
    setup_di_container()
    logger.info("🚀 Приложение запущено", extra={"event": "startup"})
    yield
    logger.info("🔒 Приложение остановлено", extra={"event": "shutdown"})


app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
)

# Регистрация обработчиков исключений
register_exception_handlers(app)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение статических файлов
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Подключение роутеров новой архитектуры
app.include_router(auth_router, prefix="/api/v2")
app.include_router(browser_logs_router)  # Без префикса, так как уже есть в роутере
app.include_router(content_router, prefix="/api/v2")
app.include_router(theory_router, prefix="/api/v2")
app.include_router(task_router, prefix="/api/v2")
app.include_router(progress_router, prefix="/api/v2")
app.include_router(code_editor_router, prefix="/api/v2/code-editor")
app.include_router(stats_router, prefix="/api/v2/stats")
app.include_router(mindmap_router, prefix="/api/v2/mindmap")
app.include_router(admin_router, prefix="/api/v2/admin")

# Старые роутеры удалены - используется только новая архитектура v2

# Алиасы для обратной совместимости с фронтендом удалены


# OpenAPI генерация
@app.get("/openapi.json", include_in_schema=False)
async def get_openapi():
    """Генерация OpenAPI спецификации для фронтенда"""
    openapi_schema = app.openapi()
    return JSONResponse(content=openapi_schema)


# Корневые endpoints
@app.get("/")
async def root():
    return {
        "message": f"Hello World! {settings.app_name} {settings.app_version} (NEW ARCHITECTURE)"
    }


@app.get("/api/")
async def api_root():
    return {
        "message": f"Hello World! {settings.app_name} {settings.app_version} (NEW ARCHITECTURE)"
    }


# Редирект на главную страницу
@app.get("/redirect")
async def redirect():
    return RedirectResponse(url="/")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        reload_excludes=["logs/*", "*.log"],
    )
