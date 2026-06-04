from dataclasses import dataclass

from order_service.src.domain.value_objects.object_ids import (
    ProductId,
    UserId,
    OrderId,
    OrderItemId,
)
from order_service.src.domain.value_objects.money import Money


class Command:
    order_id: OrderId


@dataclass(frozen=True)
class CreateOrderCommand(Command):
    user_id: UserId


@dataclass(frozen=True)
class AddItemCommand(Command):
    order_id: OrderId
    product_id: ProductId
    qty: int
    unit_price: Money


@dataclass(frozen=True)
class RemoveItemCommand(Command):
    order_id: OrderId
    item_id: OrderItemId


@dataclass(frozen=True)
class ChangeItemQuantityCommand(Command):
    order_id: OrderId
    item_id: OrderItemId
    qty: int


@dataclass(frozen=True)
class ConfirmOrderCommand(Command):
    order_id: OrderId


@dataclass(frozen=True)
class CancelOrderCommand(Command):
    order_id: OrderId
