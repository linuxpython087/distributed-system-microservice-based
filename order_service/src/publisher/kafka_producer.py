import json
import logging

from confluent_kafka import Producer

logger = logging.getLogger(__name__)


class KafkaEventProducer:

    def __init__(self, bootstrap_servers: str):

        self.producer = Producer(
            {
                "bootstrap.servers": bootstrap_servers,
                "enable.idempotence": True,
                "acks": "all",
                "retries": 10,
                "compression.type": "snappy",
            }
        )

    def publish(
        self,
        topic: str,
        key: str,
        payload: dict,
    ):

        self.producer.produce(
            topic=topic,
            key=key,
            value=json.dumps(payload),
        )

        self.producer.flush()
