from pydantic import BaseModel
from uuid import UUID


class CreateOrderResponse(BaseModel):
    order_id: UUID
    idempotency_key: str


class MessageResponse(BaseModel):
    message: str


class AddItemResponse(BaseModel):
    item_id: str
    message: str


class RemoveItemResponse(BaseModel):
    message: str


class ChangeQuantityResponse(BaseModel):
    message: str


class ConfirmOrderResponse(BaseModel):
    message: str


class CancelOrderResponse(BaseModel):
    message: str


class OrderDetailResponse(BaseModel):
    order_id: UUID
    user_id: UUID
    status: str
    version: int
    items: list
