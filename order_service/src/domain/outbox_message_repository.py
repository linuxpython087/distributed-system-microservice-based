from typing import Protocol
from order_service.src.domain.entities.outbox_message import OutboxMessage
from order_service.src.domain.value_objects.object_ids import OutboxId


class AbstractOutboxMessageRepository(Protocol):

    def add(self, message: OutboxMessage):
        pass

    def get_outbox_ùessage(self, id: OutboxId) -> OutboxMessage:
        pass

    def get_pending_messages(self, limit: int, skip: int = 0):
        pass

    def mark_published(self, event_id):
        pass

    def mark_failed(self, event_id, error):
        pass

    def get_retryable_messages(
        self,
        limit: int = 100,
    ):
        pass

    def claim_pending_messages(
        self,
        limit: int,
        worker_id: str,
    ) -> list[OutboxMessage]:
        pass
