# order_service/src/domain/events/order_events.py

from dataclasses import dataclass

from order_service.src.domain.value_objects.object_ids import (
    OrderId,
    UserId,
    ProductId,
    OrderItemId,
)


@dataclass(frozen=True)
class OrderCreatedEvent:
    order_id: OrderId
    user_id: UserId


@dataclass(frozen=True)
class OrderItemAddedEvent:
    order_id: OrderId
    item_id: OrderItemId
    product_id: ProductId
    quantity: int


@dataclass(frozen=True)
class OrderItemRemovedEvent:
    order_id: OrderId
    item_id: OrderItemId


@dataclass(frozen=True)
class OrderItemQuantityChangedEvent:
    order_id: OrderId
    item_id: OrderItemId
    quantity: int


@dataclass(frozen=True)
class OrderConfirmedEvent:
    order_id: OrderId
    user_id: UserId


@dataclass(frozen=True)
class OrderCancelledEvent:
    order_id: OrderId
    user_id: UserId
