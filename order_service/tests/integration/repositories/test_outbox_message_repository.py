from order_service.src.infrastructure.outbox_message_repository import SqlalchemyOutboxMessageRepository
from order_service.src.domain.aggregates.order import Order
from order_service.src.domain.value_objects.money import Money
from order_service.src.domain.order_status import OrderStatus
import pytest

from order_service.src.domain.entities.outbox_message import OutboxMessage
from order_service.src.domain.value_objects.object_ids import OutboxId

from order_service.src.domain.value_objects.object_ids import (
    ProductId,
    UserId,
    OutboxId,
    EventId,
    
)



from order_service.src.domain.value_objects.money import Money
from order_service.src.domain.entities.evenet_builder import OrderIntegrationEventFactory
from order_service.src.domain.outbox_status import OutboxStatus

from order_service.src.domain.aggregates.order import Order


def test_create_outbox_message_from_event_and_save_it_to_db(session):
    repo = SqlalchemyOutboxMessageRepository(session)

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

    repo.add(outbox)
    outbox_retrieve = repo.get_outbox_message(outbox.id)
 
    assert outbox_retrieve.event_id == integration_event.event_id

    assert outbox_retrieve.event_type == "OrderConfirmedEvent"

    assert outbox_retrieve.status == OutboxStatus.PENDING

    assert outbox_retrieve.retry_count == 0





def test_create_outbox_message_from_event_cancelled_and_save_it(session):
    repo = SqlalchemyOutboxMessageRepository(session)

    order = Order(
    user_id=UserId.new()
)

    order.cancel()

    integration_event = OrderIntegrationEventFactory.from_order(order)

    outbox = OutboxMessage.from_integration_event(integration_event, order.id)

    repo.add(outbox)
    outbox_retrieve = repo.get_outbox_message(outbox.id)
 
    assert outbox_retrieve.event_id == integration_event.event_id

    assert outbox_retrieve.event_type == "OrderCancelledEvent"

    assert outbox_retrieve.status == OutboxStatus.PENDING

    assert outbox_retrieve.retry_count == 0

