from typing import Protocol
from order_service.src.domain.entities.outbox_message import OutboxMessage
from order_service.src.domain.value_objects.object_ids import OutboxId
class AbstractOutboxMessageRepository(Protocol):

    def add(self, message: OutboxMessage):
        pass

    def get_outbox_ùessage(self, id:OutboxId) -> OutboxMessage:
        pass