import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("audit")


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start

        if request.method in ("POST", "PUT", "DELETE", "PATCH"):
            path = request.url.path
            if path.startswith("/api/v1/") and not path.startswith("/api/v1/auth/"):
                logger.info(
                    "audit: method=%s path=%s status=%s duration=%.3fs user_agent=%s",
                    request.method,
                    path,
                    response.status_code,
                    duration,
                    request.headers.get("user-agent", ""),
                )

        return response
