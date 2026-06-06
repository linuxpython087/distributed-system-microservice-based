from order_service.src.domain.entities.order_item import OrderItem
from order_service.src.domain.exceptions import InvalidOrderState
from order_service.src.domain.order_status import OrderStatus
from order_service.src.domain.value_objects.money import Money
from order_service.src.domain.value_objects.object_ids import OrderId, OrderItemId
from order_service.src.domain.events.order_events import (
    OrderCreatedEvent,
    OrderCancelledEvent,
    OrderConfirmedEvent,
    OrderItemAddedEvent,
    OrderItemQuantityChangedEvent,
    OrderItemRemovedEvent,
)

from order_service.src.domain.order_transitions import (
    ALLOWED_TRANSITIONS,
)


class Order:

    def __init__(self, user_id, order_id=None):
        self.id = order_id or OrderId.new()
        self.user_id = user_id
        self.status = OrderStatus.PENDING
        self.items = {}
        self.events = []
        self.version = 0

        self._record_event(OrderCreatedEvent(order_id=self.id, user_id=self.user_id))

    def _record_event(self, event):
        self.events.append(event)

    # -------------------------
    # behavior
    # -------------------------
    def add_item(self, product_id, qty, unit_price):
        self._ensure_modifiable()
        self._ensure_not_cancelled()

        if self.items:
            existing_currency = next(iter(self.items.values())).unit_price.currency

            if unit_price.currency != existing_currency:
                raise ValueError("Currency mismatch in order")

        item = OrderItem(product_id, qty, unit_price)

        self.items[item.id] = item
        self.version += 1
        self._record_event(OrderItemAddedEvent(self.id, item.id, product_id, qty))
        return item.id

    def remove_item(self, item_id: OrderItemId):
        self._ensure_modifiable()
        self._ensure_not_cancelled()

        del self.items[item_id]
        self.version += 1
        self._record_event(OrderItemRemovedEvent(self.id, item_id))

    def change_item_quantity(self, item_id: OrderItemId, qty):
        self._ensure_modifiable()
        self._ensure_not_cancelled()

        self.items[item_id].change_quantity(qty)
        self.version += 1
        self._record_event(OrderItemQuantityChangedEvent(self.id, item_id, qty))

    def confirm(self):
        # self._ensure_modifiable()

        self._ensure_has_items()
        self._change_status(OrderStatus.CONFIRMED)

        self.status = OrderStatus.CONFIRMED
        # self.version += 1
        self._record_event(OrderConfirmedEvent(self.id, self.user_id))

    def cancel(self):
        if self.status == OrderStatus.CANCELLED:
            return

        self._change_status(OrderStatus.CANCELLED)

        self._record_event(OrderCancelledEvent(self.id, self.user_id))

        
    def total(self) -> Money:
        items = list(self.items.values())

        if not items:
            return Money(0, "USD")

        total = items[0].subtotal()

        for item in items[1:]:
            total = total.add(item.subtotal())

        return total

    def to_dict(self):
        return {
            "order_id": str(self.id),
            "user_id": str(self.user_id),
            "version": self.version,
            "items": [
                {
                    "item_id": str(item.id),
                    "product_id": str(item.product_id),
                    "quantity": item.quantity,
                    "unit_price": {
                        "amount": item.unit_price.amount,
                        "currency": item.unit_price.currency,
                    },
                }
                for item in self.items.values()
            ],
            "status": self.status.value,
        }

    def _ensure_modifiable(self):
        if self.status != OrderStatus.PENDING:
            raise InvalidOrderState(
                f"Operation not allowed in status {self.status.value}"
            )

    def _ensure_has_items(self):
        if not self.items:
            raise InvalidOrderState("Cannot confirm empty order")

    # -------------------------
    # invariant check
    # -------------------------
    def _ensure_not_cancelled(self):
        if self.status == OrderStatus.CANCELLED:
            raise InvalidOrderState("Order is cancelled")

    def _change_status(self, new_status):
        allowed = ALLOWED_TRANSITIONS[self.status]

        if new_status not in allowed:
            raise InvalidOrderState(
                f"Transition {self.status.value} -> {new_status.value} not allowed"
            )

        self.status = new_status
        self.version += 1
