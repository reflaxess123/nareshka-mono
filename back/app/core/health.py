"""
Health check system for monitoring application components.
Provides endpoints and utilities for health monitoring.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from fastapi import APIRouter

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import redis
from redis.exceptions import RedisError

from app.shared.database import get_database_manager, check_database_health
from app.core.settings import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = Settings()


class HealthStatus(str, Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ComponentHealth:
    """Health status of a single component."""
    name: str
    status: HealthStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    response_time_ms: Optional[float] = None
    last_checked: Optional[datetime] = None


@dataclass
class SystemHealth:
    """Overall system health status."""
    status: HealthStatus
    timestamp: datetime
    components: List[ComponentHealth]
    
    @property
    def is_healthy(self) -> bool:
        """Check if system is healthy."""
        return self.status == HealthStatus.HEALTHY
    
    @property
    def unhealthy_components(self) -> List[ComponentHealth]:
        """Get list of unhealthy components."""
        return [c for c in self.components if c.status == HealthStatus.UNHEALTHY]


class HealthChecker:
    """Health checker for system components."""
    
    def __init__(self):
        self.redis_client = None
        self.setup_redis()
        
    def setup_redis(self):
        """Setup Redis client for health checks."""
        try:
            if settings.redis_url:
                self.redis_client = redis.from_url(
                    settings.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
        except Exception as e:
            logger.warning("Failed to setup Redis client for health checks", extra={
                "error": str(e)
            })
    
    async def check_database(self) -> ComponentHealth:
        """Check database connectivity and performance."""
        start_time = datetime.now()
        
        try:
            db_manager = get_database_manager()
            
            # Test basic connectivity
            with db_manager.get_session() as session:
                result = session.execute(text("SELECT 1")).scalar()
                
                if result != 1:
                    return ComponentHealth(
                        name="database",
                        status=HealthStatus.UNHEALTHY,
                        message="Database query returned unexpected result",
                        response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                        last_checked=datetime.now()
                    )
            
            # Test performance with a simple query
            with db_manager.get_session() as session:
                session.execute(text("SELECT COUNT(*) FROM information_schema.tables")).scalar()
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if response_time > 1000:  # More than 1 second
                status = HealthStatus.DEGRADED
                message = f"Database responding slowly ({response_time:.0f}ms)"
            else:
                status = HealthStatus.HEALTHY
                message = "Database is healthy"
            
            return ComponentHealth(
                name="database",
                status=status,
                message=message,
                details={
                    "driver": "postgresql",
                    "pool_size": db_manager.pool_size,
                    "max_overflow": db_manager.max_overflow
                },
                response_time_ms=response_time,
                last_checked=datetime.now()
            )
            
        except SQLAlchemyError as e:
            logger.error("Database health check failed", extra={"error": str(e)})
            return ComponentHealth(
                name="database",
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}",
                response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                last_checked=datetime.now()
            )
        except Exception as e:
            logger.error("Unexpected error in database health check", extra={"error": str(e)})
            return ComponentHealth(
                name="database",
                status=HealthStatus.UNKNOWN,
                message=f"Unexpected error: {str(e)}",
                response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                last_checked=datetime.now()
            )
    
    async def check_redis(self) -> ComponentHealth:
        """Check Redis connectivity and performance."""
        start_time = datetime.now()
        
        if not self.redis_client:
            return ComponentHealth(
                name="redis",
                status=HealthStatus.UNKNOWN,
                message="Redis client not configured",
                last_checked=datetime.now()
            )
        
        try:
            # Test basic connectivity
            await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.ping
            )
            
            # Test set/get operation
            test_key = "health_check_test"
            test_value = str(datetime.now().timestamp())
            
            await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.set, test_key, test_value, "EX", 60
            )
            
            retrieved_value = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.get, test_key
            )
            
            if retrieved_value != test_value:
                return ComponentHealth(
                    name="redis",
                    status=HealthStatus.UNHEALTHY,
                    message="Redis set/get operation failed",
                    response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                    last_checked=datetime.now()
                )
            
            # Clean up test key
            await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.delete, test_key
            )
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if response_time > 500:  # More than 500ms
                status = HealthStatus.DEGRADED
                message = f"Redis responding slowly ({response_time:.0f}ms)"
            else:
                status = HealthStatus.HEALTHY
                message = "Redis is healthy"
            
            # Get Redis info
            info = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.info
            )
            
            return ComponentHealth(
                name="redis",
                status=status,
                message=message,
                details={
                    "version": info.get("redis_version", "unknown"),
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory_human": info.get("used_memory_human", "unknown")
                },
                response_time_ms=response_time,
                last_checked=datetime.now()
            )
            
        except RedisError as e:
            logger.error("Redis health check failed", extra={"error": str(e)})
            return ComponentHealth(
                name="redis",
                status=HealthStatus.UNHEALTHY,
                message=f"Redis connection failed: {str(e)}",
                response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                last_checked=datetime.now()
            )
        except Exception as e:
            logger.error("Unexpected error in Redis health check", extra={"error": str(e)})
            return ComponentHealth(
                name="redis",
                status=HealthStatus.UNKNOWN,
                message=f"Unexpected error: {str(e)}",
                response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                last_checked=datetime.now()
            )
    
    async def check_system_resources(self) -> ComponentHealth:
        """Check system resources (memory, disk, etc.)."""
        start_time = datetime.now()
        
        try:
            import psutil
            
            # Check memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Check disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Determine status based on usage
            if memory_percent > 90 or disk_percent > 90:
                status = HealthStatus.UNHEALTHY
                message = "Critical resource usage"
            elif memory_percent > 80 or disk_percent > 80:
                status = HealthStatus.DEGRADED
                message = "High resource usage"
            else:
                status = HealthStatus.HEALTHY
                message = "System resources OK"
            
            return ComponentHealth(
                name="system_resources",
                status=status,
                message=message,
                details={
                    "memory_percent": memory_percent,
                    "memory_available_gb": round(memory.available / (1024**3), 2),
                    "disk_percent": round(disk_percent, 1),
                    "disk_free_gb": round(disk.free / (1024**3), 2)
                },
                response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                last_checked=datetime.now()
            )
            
        except ImportError:
            return ComponentHealth(
                name="system_resources",
                status=HealthStatus.UNKNOWN,
                message="psutil not available for resource monitoring",
                last_checked=datetime.now()
            )
        except Exception as e:
            logger.error("System resources health check failed", extra={"error": str(e)})
            return ComponentHealth(
                name="system_resources",
                status=HealthStatus.UNKNOWN,
                message=f"Resource check failed: {str(e)}",
                response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                last_checked=datetime.now()
            )
    
    async def check_application(self) -> ComponentHealth:
        """Check application-specific health."""
        start_time = datetime.now()
        
        try:
            # Check if critical services can be imported
            from app.shared.database import get_session
            from app.core.settings import get_settings
            
            # Verify settings are loaded
            app_settings = Settings()
            if not app_settings:
                return ComponentHealth(
                    name="application",
                    status=HealthStatus.UNHEALTHY,
                    message="Application settings not loaded",
                    last_checked=datetime.now()
                )
            
            return ComponentHealth(
                name="application",
                status=HealthStatus.HEALTHY,
                message="Application is healthy",
                details={
                    "environment": app_settings.environment.value,
                    "debug": app_settings.debug,
                    "version": getattr(app_settings, 'version', 'unknown')
                },
                response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                last_checked=datetime.now()
            )
            
        except Exception as e:
            logger.error("Application health check failed", extra={"error": str(e)})
            return ComponentHealth(
                name="application",
                status=HealthStatus.UNHEALTHY,
                message=f"Application check failed: {str(e)}",
                response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                last_checked=datetime.now()
            )
    
    async def check_all(self) -> SystemHealth:
        """Check all system components."""
        logger.info("Starting comprehensive health check")
        
        # Run all checks concurrently
        results = await asyncio.gather(
            self.check_database(),
            self.check_redis(),
            self.check_system_resources(),
            self.check_application(),
            return_exceptions=True
        )
        
        components = []
        for result in results:
            if isinstance(result, ComponentHealth):
                components.append(result)
            else:
                # Handle exceptions from health checks
                logger.error("Health check failed with exception", extra={
                    "error": str(result)
                })
                components.append(ComponentHealth(
                    name="unknown",
                    status=HealthStatus.UNKNOWN,
                    message=f"Health check exception: {str(result)}",
                    last_checked=datetime.now()
                ))
        
        # Determine overall system status
        if all(c.status == HealthStatus.HEALTHY for c in components):
            overall_status = HealthStatus.HEALTHY
        elif any(c.status == HealthStatus.UNHEALTHY for c in components):
            overall_status = HealthStatus.UNHEALTHY
        elif any(c.status == HealthStatus.DEGRADED for c in components):
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.UNKNOWN
        
        system_health = SystemHealth(
            status=overall_status,
            timestamp=datetime.now(),
            components=components
        )
        
        logger.info("Health check completed", extra={
            "overall_status": overall_status.value,
            "components_checked": len(components),
            "unhealthy_components": len(system_health.unhealthy_components)
        })
        
        return system_health


# Global health checker instance
_health_checker = None


def get_health_checker() -> HealthChecker:
    """Get the global health checker instance."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker


async def quick_health_check() -> Dict[str, Any]:
    """Perform a quick health check for liveness probe."""
    try:
        # Just check if we can import core modules
        from app.core.settings import get_settings
        settings = get_settings()
        
        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "environment": settings.environment.value
        }
    except Exception as e:
        logger.error("Quick health check failed", extra={"error": str(e)})
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        } 

"""Роутер проверки здоровья сервиса"""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy", "version": "2.0.0", "architecture": "new"} 

