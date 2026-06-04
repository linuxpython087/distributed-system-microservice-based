# order_service/src/domain/events/order_events.py

from dataclasses import dataclass

from order_service.src.domain.value_objects.object_ids import (
    OrderId,
    UserId,
    ProductId,
    OrderItemId,
)


class Event:
    pass


@dataclass(frozen=True)
class OrderCreatedEvent:
    order_id: OrderId
    user_id: UserId


@dataclass(frozen=True)
class OrderItemAddedEvent(Event):
    order_id: OrderId
    item_id: OrderItemId
    product_id: ProductId
    quantity: int


@dataclass(frozen=True)
class OrderItemRemovedEvent(Event):
    order_id: OrderId
    item_id: OrderItemId


@dataclass(frozen=True)
class OrderItemQuantityChangedEvent(Event):
    order_id: OrderId
    item_id: OrderItemId
    quantity: int


@dataclass(frozen=True)
class OrderConfirmedEvent(Event):
    order_id: OrderId
    user_id: UserId


@dataclass(frozen=True)
class OrderCancelledEvent(Event):
    order_id: OrderId
    user_id: UserId
