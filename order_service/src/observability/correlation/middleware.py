from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware

from order_service.src.observability.correlation.context import (
    bind_correlation_id,
    clear_context,
)


class CorrelationIdMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        clear_context()

        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid4())

        bind_correlation_id(correlation_id)

        response = await call_next(request)

        response.headers["X-Correlation-ID"] = correlation_id

        return response
