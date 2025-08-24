#!/usr/bin/env python3
"""FastAPI приложение nareshka"""

import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.core.error_handlers import register_exception_handlers
from app.core.logging import get_logger, init_default_logging
from app.core.settings import settings
from app.features.admin.api.admin_router import router as admin_router
from app.features.auth.api.auth_router import router as auth_router
from app.features.code_editor.api import router as code_editor_router
from app.features.content.api import router as content_router
from app.features.interviews.api.categories_router import router as categories_router
from app.features.interviews.api.companies_router import router as companies_router
from app.features.interviews.api.interviews_router import router as interviews_router
from app.features.logs.api.logs_router import (
    router as logs_router,
    setup_websocket_logging,
    disable_websocket_logging,
)
from app.features.mindmap.api import router as mindmap_router
from app.features.progress.api import router as progress_router
from app.features.stats.api import router as stats_router

from app.features.task.api import router as task_router
from app.features.theory.api import router as theory_router
from app.features.visualization.api import router as cluster_viz_router
from app.shared.di import setup_di_container

init_default_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_di_container()
    setup_websocket_logging()  # Включено обратно с исправлениями
    logger.info("🚀 Приложение запущено", extra={"event": "startup"})
    yield
    disable_websocket_logging()  # Корректное отключение при shutdown
    logger.info("🔒 Приложение остановлено", extra={"event": "shutdown"})


app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
)

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth_router, prefix="/api/v2")
app.include_router(logs_router)
app.include_router(content_router, prefix="/api/v2")
app.include_router(interviews_router, prefix="/api/v2")
app.include_router(categories_router, prefix="/api/v2")
app.include_router(companies_router, prefix="/api/v2")
app.include_router(cluster_viz_router, prefix="/api/v2")
app.include_router(theory_router, prefix="/api/v2")
app.include_router(task_router, prefix="/api/v2")
app.include_router(progress_router, prefix="/api/v2")
app.include_router(code_editor_router, prefix="/api/v2/code-editor")
app.include_router(stats_router, prefix="/api/v2/stats")
app.include_router(mindmap_router, prefix="/api/v2/mindmap")
app.include_router(admin_router, prefix="/api/v2/admin")

analytics_out_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "sobes-analysis", "out")
)
if os.path.isdir(analytics_out_dir):
    app.mount(
        "/analytics-static",
        StaticFiles(directory=analytics_out_dir),
        name="analytics-static",
    )


@app.get("/openapi.json", include_in_schema=False)
async def get_openapi():
    """Генерация OpenAPI спецификации для фронтенда"""
    openapi_schema = app.openapi()
    return JSONResponse(content=openapi_schema)


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


@app.get("/redirect")
async def redirect():
    return RedirectResponse(url="/")


@app.get("/api/test-companies")
async def get_top_companies_simple():
    return [{"name": "test", "count": 123}]


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        reload_excludes=["logs/*", "*.log", "app/features/*/tests/*"],
    )
