from dataclasses import dataclass

from order_service.src.domain.value_objects.object_ids import (
    ProductId,
    UserId,
    OrderId,
    OrderItemId,
)
from order_service.src.domain.value_objects.money import Money

from dataclasses import asdict, is_dataclass


class Command:

    def _serialize(self, value):

        if hasattr(value, "value"):
            return str(value.value)

        if is_dataclass(value):
            return {k: self._serialize(v) for k, v in asdict(value).items()}

        if isinstance(value, dict):
            return {k: self._serialize(v) for k, v in value.items()}

        if isinstance(value, list):
            return [self._serialize(v) for v in value]

        return value

    def to_dict(self):

        return {key: self._serialize(value) for key, value in self.__dict__.items()}


@dataclass(frozen=True)
class CreateOrderCommand(Command):
    user_id: UserId
    # idempotency_key: str


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
