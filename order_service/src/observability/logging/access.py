import structlog

logger = structlog.get_logger()


def log_request():

    logger.info("http_request")
