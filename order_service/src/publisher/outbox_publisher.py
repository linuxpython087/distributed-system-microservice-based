import logging

from order_service.src.infrastructure.outbox_message_repository import (
    SqlalchemyOutboxMessageRepository
)


logger = logging.getLogger(__name__)

class OutboxPublisher:

    def __init__(
        self,
        repository,
        producer,
        topic_name,
        worker_id,
    ):
        self.repository = repository
        self.producer = producer
        self.topic_name = topic_name
        self.worker_id = worker_id

    def publish_pending_messages(self):

        messages = self.repository.claim_pending_messages(
                limit=100,
                worker_id=self.worker_id,
            )
        

        for msg in messages:

            try:

                payload = {
                    "event_id": str(msg.event_id),
                    "event_type": msg.event_type,
                    "aggregate_id": str(msg.aggregate_id),
                    "payload": msg.payload,
                }

                self.producer.publish(
                    topic=self.topic_name,
                    key=str(msg.event_id),
                    payload=payload,
                )

                self.repository.mark_published(
                    msg.event_id
                )
                self.repository.session.commit()

            except Exception as e:

                self.repository.mark_failed(
                    msg.event_id,
                    str(e)
                )
                self.repository.session.commit()

        return len(messages)