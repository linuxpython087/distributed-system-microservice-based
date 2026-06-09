# domain/entities/outbox_message.py

from dataclasses import dataclass
from datetime import datetime

from order_service.src.domain.value_objects.object_ids import (
    OutboxId,
    EventId,
)
from order_service.src.domain.outbox_status import OutboxStatus


@dataclass
class OutboxMessage:

    id: OutboxId

    event_id: EventId

    aggregate_id: str

    event_type: str

    payload: dict

    status: OutboxStatus

    created_at: datetime

    published_at: datetime | None

    retry_count: int

    max_retries: int = 5

    failed_at: datetime | None = None

    locked_at: datetime | None = None

    locked_by: str | None = None

    last_error: str | None = None

    sequence_number: int | None = None

    @classmethod
    def from_integration_event(cls, event, aggregate_id: str):
        return cls(
            id=OutboxId.new(),
            event_id=event.event_id,
            aggregate_id=str(aggregate_id),
            event_type=event.event_type,
            payload=event.to_dict(),
            status=OutboxStatus.PENDING,
            created_at=datetime.now(),
            published_at=None,
            retry_count=0,
        )
