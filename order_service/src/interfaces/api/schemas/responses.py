from pydantic import BaseModel
from uuid import UUID


class CreateOrderResponse(BaseModel):
    order_id: UUID