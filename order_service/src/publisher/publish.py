from confluent_kafka import Producer
import json
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s - %(levelname)s - %(message)s"
)


producer_config = {
    "bootstrap.servers": "localhost:9092",

    # Reliability
    "enable.idempotence": True,
    "acks": "all",
    "retries": 10,

    # Throughput
    "batch.size": 32768,
    "linger.ms": 5,

    # Compression
    "compression.type": "snappy",
}

producer = Producer(producer_config)

order = {
    "order_id": 1,
    "user": "Tchalim",
    "item": "Apple",
    "quantity": 18,
    "unit_price": 1000
}

def delivery_report(err, msg):
    if err:
        logging.error(f"Delivery failed: {err}")
    else:
        logging.info(
            f"Delivered to partition {msg.partition()} "
            f"offset {msg.offset()}"
        )

producer.produce(
    topic="example_topics",
    key=str(order["order_id"]),
    value=json.dumps(order),
    callback=delivery_report,
    partition=0
)

producer.flush()