# interfaces/api/views.py

from fastapi import APIRouter, Depends
from order_service.src.read_model.repository import OrderReadRepository
from order_service.src.infrastructure.database import get_db

router = APIRouter()

from opentelemetry import trace

tracer = trace.get_tracer(__name__)


    

@router.get("/orders/{order_id}")
def get_order(order_id: str, session=Depends(get_db)):

    with tracer.start_as_current_span("create_order_usecase") as span:
        span.set_attribute("order.customer_id", order_id)

        repo = OrderReadRepository(session)

        span.set_attribute("order.id", order_id)

        return repo.get_order(order_id)


   
