"""
Health check system for monitoring application components.
Provides endpoints and utilities for health monitoring.
"""

from datetime import datetime
from typing import Any, Dict

from app.core.logging import get_logger
from app.core.settings import settings

logger = get_logger(__name__)


async def quick_health_check() -> Dict[str, Any]:
    """Perform a quick health check for liveness probe."""
    try:
        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "environment": settings.app_environment,
        }
    except Exception as e:
        logger.error("Quick health check failed", extra={"error": str(e)})
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }
