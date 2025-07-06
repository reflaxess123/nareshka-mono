"""Роутер проверки здоровья сервиса"""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy", "version": "2.0.0", "architecture": "new"}


@router.get("/")
async def root():
    """Базовый endpoint"""
    return {"message": "Hello World! Nareshka API v2.0 (NEW ARCHITECTURE)"} 