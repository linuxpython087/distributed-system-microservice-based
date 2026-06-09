from order_service.src.infrastructure.outbox_message_repository import (
    SqlalchemyOutboxMessageRepository,
)
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
from order_service.src.domain.entities.evenet_builder import (
    OrderIntegrationEventFactory,
)
from order_service.src.domain.outbox_status import OutboxStatus

from order_service.src.domain.aggregates.order import Order


def test_create_outbox_message_from_event_and_save_it_to_db(session):
    repo = SqlalchemyOutboxMessageRepository(session)

    order = Order(user_id=UserId.new())

    order.add_item(product_id=ProductId.new(), qty=2, unit_price=Money(10))

    order.add_item(product_id=ProductId.new(), qty=2, unit_price=Money(100))

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

    order = Order(user_id=UserId.new())

    order.cancel()

    integration_event = OrderIntegrationEventFactory.from_order(order)

    outbox = OutboxMessage.from_integration_event(integration_event, order.id)

    repo.add(outbox)
    outbox_retrieve = repo.get_outbox_message(outbox.id)

    assert outbox_retrieve.event_id == integration_event.event_id

    assert outbox_retrieve.event_type == "OrderCancelledEvent"

    assert outbox_retrieve.status == OutboxStatus.PENDING

    assert outbox_retrieve.retry_count == 0


def test_get_pending_event(session):
    repo = SqlalchemyOutboxMessageRepository(session)

    order = Order(user_id=UserId.new())

    order.cancel()

    integration_event = OrderIntegrationEventFactory.from_order(order)

    outbox = OutboxMessage.from_integration_event(integration_event, order.id)

    repo.add(outbox)
    outbox_retrieve = repo.get_pending_messages()
    assert len(outbox_retrieve) == 1
    assert outbox_retrieve[0].status == OutboxStatus.PENDING
    assert outbox_retrieve[0].event_type == "OrderCancelledEvent"


def test_mark_message_publised(session):
    repo = SqlalchemyOutboxMessageRepository(session)

    order = Order(user_id=UserId.new())

    order.cancel()

    integration_event = OrderIntegrationEventFactory.from_order(order)

    outbox = OutboxMessage.from_integration_event(integration_event, order.id)

    repo.add(outbox)
    outbox_retrieve = repo.get_pending_messages()

    repo.mark_published(event_id=outbox_retrieve[0].event_id)
    repo.session.commit()

    published = repo.get_outbox_message(outbox.id)

    assert published.status == OutboxStatus.PUBLISHED
    assert published.published_at is not None


def test_mark_message_failed(session):
    repo = SqlalchemyOutboxMessageRepository(session)

    order = Order(user_id=UserId.new())

    order.cancel()

    integration_event = OrderIntegrationEventFactory.from_order(order)

    outbox = OutboxMessage.from_integration_event(integration_event, order.id)

    repo.add(outbox)
    outbox_retrieve = repo.get_pending_messages()

    repo.mark_failed(event_id=outbox_retrieve[0].event_id, error="Published failed")

    published = repo.get_outbox_message(outbox.id)

    assert published.status == OutboxStatus.FAILED
    assert published.failed_at is not None


def test_claim_pending_messages(session):
    repo = SqlalchemyOutboxMessageRepository(session)

    order = Order(user_id=UserId.new())

    order.cancel()

    integration_event = OrderIntegrationEventFactory.from_order(order)

    outbox = OutboxMessage.from_integration_event(integration_event, order.id)

    repo.add(outbox)

    claimed = repo.claim_pending_messages(limit=10, worker_id="worker-1")

    assert len(claimed) == 1

    assert claimed[0].status == OutboxStatus.PROCESSING

    assert claimed[0].locked_by == "worker-1"

    assert claimed[0].locked_at is not None


def test_claim_only_pending_messages(session):
    repo = SqlalchemyOutboxMessageRepository(session)

    order = Order(user_id=UserId.new())

    order.cancel()

    event = OrderIntegrationEventFactory.from_order(order)

    outbox = OutboxMessage.from_integration_event(event, order.id)

    outbox.status = OutboxStatus.FAILED

    repo.add(outbox)

    claimed = repo.claim_pending_messages(limit=10, worker_id="worker-1")

    assert claimed == []


def test_claim_respects_limit(session):
    repo = SqlalchemyOutboxMessageRepository(session)

    for _ in range(5):
        order = Order(user_id=UserId.new())

        order.cancel()

        event = OrderIntegrationEventFactory.from_order(order)

        repo.add(OutboxMessage.from_integration_event(event, order.id))

    claimed = repo.claim_pending_messages(limit=2, worker_id="worker-1")

    assert len(claimed) == 2


def test_get_retryable_messages(session):
    repo = SqlalchemyOutboxMessageRepository(session)

    order = Order(user_id=UserId.new())

    order.cancel()

    event = OrderIntegrationEventFactory.from_order(order)

    outbox = OutboxMessage.from_integration_event(event, order.id)

    outbox.status = OutboxStatus.FAILED
    outbox.retry_count = 2

    repo.add(outbox)

    messages = repo.get_retryable_messages()

    assert len(messages) == 1

    assert messages[0].status == OutboxStatus.FAILED

    assert messages[0].retry_count == 2


def test_message_with_5_retries_is_not_retryable(session):
    repo = SqlalchemyOutboxMessageRepository(session)

    order = Order(user_id=UserId.new())

    order.cancel()

    event = OrderIntegrationEventFactory.from_order(order)

    outbox = OutboxMessage.from_integration_event(event, order.id)

    outbox.status = OutboxStatus.FAILED
    outbox.retry_count = 5

    repo.add(outbox)

    messages = repo.get_retryable_messages()

    assert len(messages) == 0
