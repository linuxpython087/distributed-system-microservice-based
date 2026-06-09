# interfaces/api/views.py

from fastapi import APIRouter, Depends
from order_service.src.read_model.repository import OrderReadRepository
from order_service.src.infrastructure.database import get_db

router = APIRouter()


@router.get("/orders/{order_id}")
def get_order(order_id: str, session=Depends(get_db)):
    repo = OrderReadRepository(session)
    return repo.get_order(order_id)
