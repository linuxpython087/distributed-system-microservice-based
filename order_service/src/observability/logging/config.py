import logging
import structlog
from order_service.src.observability.logging.processors import (
    add_service_context,
    add_exception,
)


def configure_logging():

    structlog.configure(
        processors=[
            add_service_context,
            structlog.contextvars.merge_contextvars,
            add_exception,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(),
    )

    logging.basicConfig(level=logging.INFO)
