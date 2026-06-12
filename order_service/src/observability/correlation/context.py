import structlog


def bind_correlation_id(correlation_id: str):

    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)


def clear_context():

    structlog.contextvars.clear_contextvars()
