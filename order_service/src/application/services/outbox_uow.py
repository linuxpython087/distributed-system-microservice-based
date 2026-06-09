from typing import Protocol
from order_service.src.domain.outbox_message_repository import AbstractOutboxMessageRepository

class AbstractUnitOfWork(Protocol):

    outbox_messages: AbstractOutboxMessageRepository

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()


from order_service.src.infrastructure.database import SessionLocal
from order_service.src.infrastructure.outbox_message_repository import SqlalchemyOutboxMessageRepository

class SqlAlchemyUnitOfWork:

    def __init__(self):
        self.session = None
        self.outbox_messages = None

    def __enter__(self):
        self.session = SessionLocal()

        self.outbox_messages = SqlalchemyOutboxMessageRepository(
            session=self.session
        )

        return self

    def __exit__(self, *args):
        self.rollback()
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()