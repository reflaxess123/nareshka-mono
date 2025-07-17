"""
Health check system for monitoring application components.
Provides endpoints and utilities for health monitoring.
"""

from datetime import datetime
from typing import Dict, Any

from app.core.settings import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = Settings()




async def quick_health_check() -> Dict[str, Any]:
    """Perform a quick health check for liveness probe."""
    try:
        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "environment": settings.app_environment
        }
    except Exception as e:
        logger.error("Quick health check failed", extra={"error": str(e)})
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        } 


