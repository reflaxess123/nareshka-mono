from fastapi import APIRouter
from .cluster_visualization_router import router as _router

# Переэкспорт для удобного импорта на уровне пакета
router: APIRouter = _router

__all__ = ["router"]
