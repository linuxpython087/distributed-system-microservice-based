import time

from order_service.src.infrastructure.database import SessionLocal

from order_service.src.infrastructure.outbox_message_repository import (
    SqlalchemyOutboxMessageRepository
)

from order_service.src.publisher.kafka_producer import (
    KafkaEventProducer
)

from order_service.src.publisher.outbox_publisher import (
    OutboxPublisher
)
from order_service.src.infrastructure.mapper import start_mappers
from order_service.src.application.services.outbox_uow import SqlAlchemyUnitOfWork



import time
import logging

from order_service.src.infrastructure.mapper import start_mappers
from order_service.src.publisher.kafka_producer import KafkaEventProducer
from order_service.src.application.services.outbox_uow import SqlAlchemyUnitOfWork
from order_service.src.publisher.outbox_publisher import OutboxPublisher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():

    start_mappers()

    producer = KafkaEventProducer(
        bootstrap_servers="kafka:9092"
    )

    while True:

        try:
            with SqlAlchemyUnitOfWork() as uow:

                publisher = OutboxPublisher(
                    repository=uow.outbox_messages,
                    producer=producer,
                    topic_name="order_service_topics",
                    worker_id="worker-1",
                )

                count = publisher.publish_pending_messages()

                uow.commit()

                logger.info(f"Published batch: {count}")

        except Exception as e:
            logger.error(f"Worker error: {e}")

        time.sleep(2)  # polling interval


if __name__ == "__main__":
    main()