from fastapi import FastAPI

from order_service.src.interfaces.api.routers import orders

app = FastAPI(
    title="Order Service",
    version="1.0.0"
)

app.include_router(
    orders.router,
    prefix="/orders",
    tags=["Orders"]
)