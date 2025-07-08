#!/usr/bin/env python3
"""FastAPI приложение nareshka"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import json
import os
from pathlib import Path

# Инициализация логирования перед импортом других модулей
from app.core.logging import init_default_logging, get_logger
from app.core.error_handlers import register_exception_handlers

# Инициализируем логирование
init_default_logging()
logger = get_logger(__name__)

from app.config import new_settings
from app.presentation.api.health import router as health_router
from app.presentation.api.auth_v2 import router as auth_v2_router
from app.presentation.api.content_v2 import router as content_v2_router
from app.presentation.api.theory_v2 import router as theory_v2_router
from app.presentation.api.task_v2 import router as task_v2_router
from app.presentation.api.progress_v2 import router as progress_v2_router
from app.presentation.api.code_editor_v2 import router as code_editor_v2_router
from app.presentation.api.stats_v2 import router as stats_v2_router
from app.presentation.api.mindmap_v2 import router as mindmap_v2_router
from app.presentation.api.admin_v2 import router as admin_v2_router

# Импорты для алиасов совместимости удалены

# Старые роутеры удалены для полного перехода на новую архитектуру

# Событие startup - выполняется один раз при запуске приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Приложение запущено", extra={"event": "startup"})
    yield
    logger.info("🔒 Приложение остановлено", extra={"event": "shutdown"})


app = FastAPI(
    title=new_settings.app_name,
    description=new_settings.description,
    version=new_settings.version,
    lifespan=lifespan
)

# Регистрация обработчиков исключений
register_exception_handlers(app)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=new_settings.server.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение статических файлов
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Подключение роутеров новой архитектуры
app.include_router(health_router, prefix="/api")
app.include_router(auth_v2_router, prefix="/api/v2")
app.include_router(content_v2_router, prefix="/api/v2")
app.include_router(theory_v2_router, prefix="/api/v2")
app.include_router(task_v2_router, prefix="/api/v2")
app.include_router(progress_v2_router, prefix="/api/v2/progress")
app.include_router(code_editor_v2_router, prefix="/api/v2/code-editor")
app.include_router(stats_v2_router, prefix="/api/v2/stats")
app.include_router(mindmap_v2_router, prefix="/api/v2/mindmap")
app.include_router(admin_v2_router, prefix="/api/v2/admin")

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
    return {"message": f"Hello World! {new_settings.app_name} {new_settings.version} (NEW ARCHITECTURE)"}

@app.get("/api/")
async def api_root():
    return {"message": f"Hello World! {new_settings.app_name} {new_settings.version} (NEW ARCHITECTURE)"}

# Редирект на главную страницу
@app.get("/redirect")
async def redirect():
    return RedirectResponse(url="/")

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=new_settings.server.host, 
        port=new_settings.server.port, 
        reload=new_settings.server.debug
    ) 