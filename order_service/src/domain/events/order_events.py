# order_service/src/domain/events/order_events.py

from dataclasses import dataclass

from order_service.src.domain.value_objects.object_ids import (
    OrderId,
    UserId,
    ProductId,
    OrderItemId,
)


from dataclasses import dataclass, field

from order_service.src.domain.value_objects.object_ids import (
    EventId,
)



@dataclass(frozen=True, kw_only=True)
class Event:
    event_id: EventId = field(default_factory=EventId.new)

    def to_dict(self):
        result = {}

        for key, value in self.__dict__.items():

            if hasattr(value, "value"):
                result[key] = str(value.value)
            else:
                result[key] = value

        return result


@dataclass(frozen=True)
class OrderCreatedEvent(Event):
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






@dataclass
class OrderIntegrationEvent:
    event_id: EventId
    event_type: str
    order_id: str
    user_id: str
    total_amount: float
    currency: str
    items: list

    def to_dict(self):
        return {
            "event_id": str(self.event_id.value),
            "event_type": self.event_type,
            "order_id": self.order_id,
            "user_id": self.user_id,
            "total_amount": self.total_amount,
            "currency": self.currency,
            "items": self.items,
        }