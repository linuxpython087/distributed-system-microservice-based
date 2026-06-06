from fastapi import FastAPI

from order_service.src.interfaces.api.routers import orders, views

app = FastAPI(title="Order Service", version="1.0.0")


from fastapi import FastAPI
from fastapi.responses import JSONResponse

from order_service.src.domain.exceptions import (
    DomainException,
)

from fastapi.responses import JSONResponse

from order_service.src.domain.exceptions import (
    OrderNotFound,
    InvalidOrderState,
    InvalidQuantity,
)


@app.exception_handler(DomainException)
async def domain_exception_handler(
    request,
    exc,
):
    return JSONResponse(
        status_code=409,
        content={"error": str(exc)},
    )


@app.exception_handler(OrderNotFound)
async def handle_order_not_found(
    request,
    exc,
):
    return JSONResponse(
        status_code=404,
        content={
            "code": "ORDER_NOT_FOUND",
            "message": str(exc),
        },
    )


@app.exception_handler(InvalidOrderState)
async def handle_invalid_state(
    request,
    exc,
):
    return JSONResponse(status_code=409, content={"error": str(exc)})


@app.exception_handler(InvalidQuantity)
async def handle_invalid_quantity(
    request,
    exc,
):
    return JSONResponse(status_code=400, content={"error": str(exc)})


app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(views.router, prefix="/orders", tags=["Read Orders"]) 
