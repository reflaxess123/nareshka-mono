from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.shared.dependencies import get_database_session
from app.shared.logging.api_logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/browser-logs", tags=["Browser Logs"])


class BrowserLogEntry(BaseModel):
    level: str  # log, warn, error, info, debug
    message: str
    timestamp: datetime
    url: Optional[str] = None
    user_id: Optional[int] = None
    source: str = "browser"
    stack_trace: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class NetworkLogEntry(BaseModel):
    url: str
    method: str
    status_code: Optional[int] = None
    timestamp: datetime
    request_headers: Optional[Dict[str, str]] = None
    response_headers: Optional[Dict[str, str]] = None
    error_message: Optional[str] = None
    user_id: Optional[int] = None


class BrowserLogsRequest(BaseModel):
    console_logs: List[BrowserLogEntry] = []
    network_logs: List[NetworkLogEntry] = []
    page_url: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None


@router.post("/", status_code=status.HTTP_201_CREATED)
async def receive_browser_logs(logs_data: BrowserLogsRequest):
    """
    Endpoint for receiving browser logs from Browser Tools MCP server
    """
    try:
        # Логируем получение данных
        logger.info(
            f"Received browser logs: {len(logs_data.console_logs)} console logs, "
            f"{len(logs_data.network_logs)} network logs"
        )
        
        # Обрабатываем console логи
        for log_entry in logs_data.console_logs:
            logger.info(
                f"Browser Console [{log_entry.level.upper()}]: {log_entry.message}",
                extra={
                    "browser_url": log_entry.url,
                    "user_id": log_entry.user_id,
                    "timestamp": log_entry.timestamp,
                    "metadata": log_entry.metadata
                }
            )
            
            # Если это ошибка - логируем с высоким приоритетом
            if log_entry.level == "error":
                logger.error(
                    f"Browser JavaScript Error: {log_entry.message}",
                    extra={
                        "stack_trace": log_entry.stack_trace,
                        "url": log_entry.url,
                        "user_id": log_entry.user_id
                    }
                )
        
        # Обрабатываем network логи
        for network_entry in logs_data.network_logs:
            if network_entry.error_message:
                logger.warning(
                    f"Network Error: {network_entry.method} {network_entry.url} - {network_entry.error_message}",
                    extra={
                        "status_code": network_entry.status_code,
                        "user_id": network_entry.user_id
                    }
                )
        
        # TODO: Сохранить в базу данных если нужно
        # await save_to_database(logs_data)
        
        return {
            "status": "success",
            "message": "Browser logs received and processed",
            "processed": {
                "console_logs": len(logs_data.console_logs),
                "network_logs": len(logs_data.network_logs)
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing browser logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process browser logs"
        )


@router.get("/health")
async def browser_logs_health():
    """Health check for browser logs endpoint"""
    return {
        "status": "healthy",
        "service": "browser-logs",
        "timestamp": datetime.utcnow()
    }


@router.get("/stats")
async def get_browser_logs_stats():
    """Get statistics about browser logs"""
    # TODO: Implement real stats from database
    return {
        "total_logs": 0,
        "error_count": 0,
        "warning_count": 0,
        "last_updated": datetime.utcnow()
    }