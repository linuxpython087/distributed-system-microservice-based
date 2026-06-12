import time
from starlette.middleware.base import BaseHTTPMiddleware

from prometheus_client import Counter, Histogram
import structlog
from order_service.src.observability.metrics.http_metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    ERROR_COUNT,
)


class ObservabilityMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        start = time.time()

        # bind early context
        structlog.contextvars.bind_contextvars(
            method=request.method, path=request.url.path
        )

        response = await call_next(request)

        duration = time.time() - start

        if response.status_code >= 500:
            ERROR_COUNT.labels(
                method=request.method,
                path=request.url.path,
                status=response.status_code,
            ).inc()

        # metrics update (IMPORTANT PART)
        REQUEST_COUNT.labels(
            method=request.method, path=request.url.path, status=response.status_code
        ).inc()

        REQUEST_LATENCY.labels(
            method=request.method, path=request.url.path, status=response.status_code
        ).observe(duration)

        # logging context update
        structlog.contextvars.bind_contextvars(
            status_code=response.status_code, duration_ms=round(duration * 1000, 2)
        )

        return response
