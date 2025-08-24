"""
Утилиты для shared компонентов
"""

from fastapi import Request


class RequestContext:
    """Контекст запроса для логирования и трекинга"""

    def __init__(self, request: Request):
        self.request = request
        self.method = request.method
        self.url = str(request.url)
        self.client_ip = request.client.host if request.client else "unknown"
        self.user_agent = request.headers.get("user-agent", "unknown")
        self.correlation_id = request.headers.get("x-correlation-id")

    def to_dict(self) -> dict:
        """Преобразовать в словарь для логирования"""
        return {
            "method": self.method,
            "url": self.url,
            "client_ip": self.client_ip,
            "user_agent": self.user_agent,
            "correlation_id": self.correlation_id,
        }
