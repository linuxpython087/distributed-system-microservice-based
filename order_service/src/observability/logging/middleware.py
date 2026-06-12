import time
import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from order_service.src.observability.logging.access import log_request


class LoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        start = time.time()

        # 1. bind request metadata EARLY
        structlog.contextvars.bind_contextvars(
            method=request.method, path=request.url.path
        )

        response = await call_next(request)

        duration = round((time.time() - start) * 1000, 2)

        # 2. bind response metadata
        structlog.contextvars.bind_contextvars(
            status_code=response.status_code, duration_ms=duration
        )

        # 3. IMPORTANT: log AFTER full context exists
        log_request()

        return response
