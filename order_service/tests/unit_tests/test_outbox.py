from order_service.src.domain.entities.outbox_message import OutboxMessage
from order_service.src.domain.value_objects.object_ids import UserId, ProductId

from order_service.src.domain.value_objects.money import Money
from order_service.src.domain.entities.evenet_builder import OrderIntegrationEventFactory
from order_service.src.domain.outbox_status import OutboxStatus

from order_service.src.domain.aggregates.order import Order


def test_create_outbox_message_from_event():

    order = Order(
    user_id=UserId.new()
)

    order.add_item(
        product_id=ProductId.new(),
        qty=2,
        unit_price=Money(10)
    )

    order.add_item(
        product_id=ProductId.new(),
        qty=2,
        unit_price=Money(100)
    )

    order.confirm()

    integration_event = OrderIntegrationEventFactory.from_order(order)
    

    outbox = OutboxMessage.from_integration_event(integration_event, order.id)
 
    assert outbox.event_id == integration_event.event_id

    assert outbox.event_type == "OrderConfirmedEvent"

    assert outbox.status == OutboxStatus.PENDING

    assert outbox.retry_count == 0



def test_create_outbox_message_from_event_cancelled():

    order = Order(
    user_id=UserId.new()
)

    order.cancel()

    integration_event = OrderIntegrationEventFactory.from_order(order)

    outbox = OutboxMessage.from_integration_event(integration_event, order.id)
 
    assert outbox.event_id == integration_event.event_id

    assert outbox.event_type == "OrderCancelledEvent"

    assert outbox.status == OutboxStatus.PENDING

    assert outbox.retry_count == 0


