from pydantic import BaseModel
from uuid import UUID


class CreateOrderRequest(BaseModel):
    user_id: UUID


class AddItemRequest(BaseModel):
    product_id: UUID
    qty: int
    unit_price: float


class ChangeQuantityRequest(BaseModel):
    qty: int
