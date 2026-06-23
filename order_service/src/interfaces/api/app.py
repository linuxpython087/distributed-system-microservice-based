from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import socket
import structlog

from order_service.src.interfaces.api.routers import orders, views
from order_service.src.domain.exceptions import (
    DomainException,
    OrderNotFound,
    InvalidOrderState,
    InvalidQuantity,
)

from order_service.src.application.bootstrap import bootstrap
from order_service.src.observability.correlation.middleware import (
    CorrelationIdMiddleware,
)
from order_service.src.observability.logging.middleware import (
    LoggingMiddleware,
)
from order_service.src.observability.metrics.middlewares import (
    ObservabilityMiddleware,
)
from order_service.src.observability.logging.config import configure_logging

from order_service.src.observability.tracing.setup import setup_tracing

from prometheus_client import generate_latest
from fastapi import Response


logger = structlog.get_logger()

app = FastAPI(title="Order Service", version="1.0.0")


# =========================
# MIDDLEWARES
# =========================

app.add_middleware(ObservabilityMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(CorrelationIdMiddleware)


# =========================
# GLOBAL STATE
# =========================

app_state = {
    "bootstrapped": False,
    "error": None,
}


# =========================
# HEALTH SERVICE
# =========================


class HealthService:

    def __init__(self, uow):
        self.uow = uow

    def db_ok(self):

        try:
            with self.uow:
                return True

        except Exception:

            logger.exception("database_health_failed")

            return False


# =========================
# STARTUP
# =========================


@app.on_event("startup")
def startup_event():
    configure_logging()
    setup_tracing(app) 

    try:

        logger.info("application_bootstrap_started")

        bus = bootstrap()

        with bus.uow:
            pass

        app.state.bus = bus
        app.state.health = HealthService(bus.uow)

        app_state["bootstrapped"] = True
        app_state["error"] = None

        logger.info("application_bootstrap_completed")

    except Exception:

        logger.exception("application_bootstrap_failed")

        app_state["bootstrapped"] = False
        app_state["error"] = "startup failed"


# =========================
# PROBES
# =========================


@app.get("/startup")
def startup_probe():

    if not app_state["bootstrapped"]:

        logger.warning("startup_probe_failed", error=app_state["error"])

        return JSONResponse(
            status_code=500, content={"status": "starting", "error": app_state["error"]}
        )

    return {"status": "started"}


@app.get("/ready")
def readiness_probe():

    try:

        if not app_state["bootstrapped"]:

            logger.warning("readiness_failed_bootstrap")

            return JSONResponse(status_code=503, content={"ready": False})

        if not app.state.health.db_ok():

            logger.warning("readiness_failed_db")

            return JSONResponse(status_code=503, content={"ready": False})

        return {"ready": True}

    except Exception:

        logger.exception("readiness_check_crashed")

        return JSONResponse(status_code=503, content={"ready": False})


@app.get("/health")
def health_probe():

    return {
        "status": "alive",
        "hostname": socket.gethostname(),
    }


@app.get("/metrics")
def metrics():

    return Response(
        generate_latest(),
        media_type="text/plain",
    )


# =========================
# EXCEPTION HANDLERS
# =========================


@app.exception_handler(DomainException)
async def handle_domain_error(
    request: Request,
    exc: DomainException,
):

    logger.warning(
        "domain_exception", path=request.url.path, method=request.method, error=str(exc)
    )

    return JSONResponse(status_code=409, content={"error": str(exc)})


@app.exception_handler(OrderNotFound)
async def handle_order_not_found(
    request: Request,
    exc: OrderNotFound,
):

    logger.warning(
        "order_not_found", path=request.url.path, method=request.method, error=str(exc)
    )

    return JSONResponse(
        status_code=404,
        content={
            "code": "ORDER_NOT_FOUND",
            "message": str(exc),
        },
    )


@app.exception_handler(InvalidOrderState)
async def handle_invalid_state(
    request: Request,
    exc: InvalidOrderState,
):

    logger.warning("invalid_order_state", path=request.url.path, error=str(exc))

    return JSONResponse(status_code=409, content={"error": str(exc)})


@app.exception_handler(InvalidQuantity)
async def handle_invalid_quantity(
    request: Request,
    exc: InvalidQuantity,
):

    logger.warning("invalid_quantity", path=request.url.path, error=str(exc))

    return JSONResponse(status_code=400, content={"error": str(exc)})


# catch EVERYTHING


@app.exception_handler(Exception)
async def handle_unexpected(
    request: Request,
    exc: Exception,
):

    logger.exception(
        "unexpected_server_error", path=request.url.path, method=request.method
    )

    return JSONResponse(status_code=500, content={"error": "Internal Server Error"})


@app.exception_handler(Exception)
async def handle_internal_error(
    request: Request,
    exc: Exception,
):

    logger.exception(
        "internal_server_error"
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "code": "INTERNAL_SERVER_ERROR",
            "message": "Unexpected server error"
        }
    )

# =========================
# ROUTERS
# =========================

app.include_router(orders.router, prefix="/orders", tags=["Orders"])

app.include_router(views.router, prefix="/orders", tags=["Read Orders"])
