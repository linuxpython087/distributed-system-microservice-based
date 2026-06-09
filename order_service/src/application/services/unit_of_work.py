from abc import abstractmethod, ABC
from order_service.src.domain.repositories import OrderRepository
from order_service.src.infrastructure.repositories import SqlAlchemyOrderRepository

from order_service.src.infrastructure.fake_repository import FakeOrderRepository

from order_service.src.domain.idempotency.repository import (
    AbstractIdempotencyRepository,
)
from order_service.src.infrastructure.idempotency.repository import (
    IdempotencyRepository,
)
from order_service.src.infrastructure.outbox_message_repository import (
    SqlalchemyOutboxMessageRepository,
)
from order_service.src.domain.outbox_message_repository import (
    AbstractOutboxMessageRepository,
)

from order_service.src.domain.entities.outbox_message import OutboxMessage
from order_service.src.domain.entities.evenet_builder import (
    OrderIntegrationEventFactory,
)


class AbstractOrderUnitOfWork(ABC):

    orders: OrderRepository
    idempotency: AbstractIdempotencyRepository
    outbox: AbstractOutboxMessageRepository

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError

    def collect_new_events(self):

        for order in self.orders.seen:

            while order.events:

                yield order.events.pop(0)

    # def collect_new_events(self):


class FakeUnitOfWork(AbstractOrderUnitOfWork):

    def __init__(self):
        self.orders = FakeOrderRepository()
        self.committed = False
        self.rolled_back = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc:
            self.rollback()
        else:
            self.commit()

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


class SqlAlchemyOrderUnitOfWork(AbstractOrderUnitOfWork):

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.orders = SqlAlchemyOrderRepository(self.session)
        self.idempotency = IdempotencyRepository(self.session)
        self.outbox = SqlalchemyOutboxMessageRepository(self.session)
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if exc:
                self.rollback()
            else:
                self.commit()
        finally:
            self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def publish_events_to_outbox(self):
        for order in self.orders.seen:

            # 1. build integration event from ORDER (not raw event)
            integration_event = OrderIntegrationEventFactory.from_order(order)

            if integration_event is not None:

                # 2. build outbox message
                outbox_message = OutboxMessage.from_integration_event(
                    integration_event, aggregate_id=str(order.id)
                )

                # 3. persist
                self.outbox.add(outbox_message)

            else:
                pass
