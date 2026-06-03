from dataclasses import dataclass

from order_service.src.domain.value_objects.object_ids import (
    ProductId,
    UserId,
    OrderId
)
from order_service.src.domain.value_objects.money import Money


@dataclass(frozen=True)
class CreateOrderCommand:
    user_id: UserId


@dataclass(frozen=True)
class ConfirmOrderCommand:
    order_id: OrderId


@dataclass(frozen=True)
class AddItemCommand:
    order_id: OrderId
    product_id: ProductId
    qty: int
    unit_price: Money