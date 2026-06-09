
from order_service.src.domain.entities.outbox_message import OutboxMessage
from order_service.src.domain.value_objects.object_ids import OutboxId, EventId, OrderId
from sqlalchemy.orm import Session

from order_service.src.domain.outbox_status import OutboxStatus
from order_service.src.infrastructure.orm import orders_table, order_items_table, outbox_messages_table
from datetime import datetime


class SqlalchemyOutboxMessageRepository:

    def __init__(self, session:Session):
        self.session = session

    def add(self, message: OutboxMessage):
        self.session.add(message)
        

    def get_outbox_message(self, id:OutboxId) -> OutboxMessage:
        outbox = self.session.query(OutboxMessage).filter(outbox_messages_table.c.id == id).first()
        return outbox
    


    def get_pending_messages(
            self,
            limit: int = 100,
        ) -> list[OutboxMessage]:

            return (
                self.session.query(OutboxMessage)
                .filter(
                    outbox_messages_table.c.status
                    == OutboxStatus.PENDING
                )
                .order_by(
                    outbox_messages_table.c.created_at.asc()
                )
                .limit(limit)
                .all()
            )

    # =====================================
    # MULTI WORKER SAFE
    # =====================================

    def claim_pending_messages(
        self,
        limit: int,
        worker_id: str,
    ) -> list[OutboxMessage]:

        messages = (
            self.session.query(OutboxMessage)
            .filter(
                outbox_messages_table.c.status
                == OutboxStatus.PENDING
            )
            .order_by(
                outbox_messages_table.c.created_at.asc()
            )
            .with_for_update(skip_locked=True)
            .limit(limit)
            .all()
        )

        now = datetime.now()

        for msg in messages:

            msg.status = OutboxStatus.PROCESSING

            msg.locked_at = now

            msg.locked_by = worker_id

        return messages

    # =====================================
    # SUCCESS
    # =====================================

    def mark_published(
        self,
        event_id: EventId,
    ):

        msg = (
            self.session.query(OutboxMessage)
            .filter(
                outbox_messages_table.c.event_id
                == event_id
            )
            .one()
        )
        if msg is not None:

            msg.status = OutboxStatus.PUBLISHED

            msg.published_at = datetime.now()

    # =====================================
    # FAILURE
    # =====================================

    def mark_failed(
        self,
        event_id: EventId,
        error: str,
    ):

        msg = (
            self.session.query(OutboxMessage)
            .filter(
                outbox_messages_table.c.event_id
                == event_id
            )
            .first()
        )
        if msg is not None:

            msg.status = OutboxStatus.FAILED

            msg.retry_count += 1

            msg.last_error = error
            msg.failed_at = datetime.now()

    # =====================================
    # RETRYABLE
    # =====================================

    def get_retryable_messages(
        self,
        limit: int = 100,
    ):

        return (
            self.session.query(OutboxMessage)
            .filter(
                outbox_messages_table.c.status
                == OutboxStatus.FAILED
            )
            .filter(
                outbox_messages_table.c.retry_count < 5
            )
            .order_by(
                outbox_messages_table.c.created_at.asc()
            )
            .limit(limit)
            .all()
        )