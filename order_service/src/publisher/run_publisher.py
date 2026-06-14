import time


from order_service.src.publisher.kafka_producer import KafkaEventProducer

from order_service.src.publisher.outbox_publisher import OutboxPublisher
from order_service.src.infrastructure.mapper import start_mappers
from order_service.src.application.services.outbox_uow import SqlAlchemyUnitOfWork

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():

    start_mappers()

    import os

    bootstrap = os.getenv("KAFKA_BOOTSTRAP", "kafka.messaging.svc.cluster.local:9092")

    producer = KafkaEventProducer(bootstrap_servers=bootstrap)

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
