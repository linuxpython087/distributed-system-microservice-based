from order_service.src.domain.events.order_events import OrderIntegrationEvent
from order_service.src.domain.value_objects.object_ids import EventId


class OrderIntegrationEventFactory:

    @staticmethod
    def from_order(order):
        if len(order.events) > 0:
            event = order.events[-1]

            return OrderIntegrationEvent(
                event_id=event.event_id,
                event_type=type(event).__name__,
                order_id=str(event.order_id),
                user_id=str(order.user_id),
                total_amount=order.total().amount,
                currency=order.total().currency,
                items=[
                    {
                        "product_id": str(item.product_id),
                        "quantity": item.quantity,
                        "unit_price": item.unit_price.amount,
                        "currency": item.unit_price.currency,
                        "subtotal": item.subtotal().amount,
                    }
                    for item in order.items.values()
                ],
            )
        else:
            return None
