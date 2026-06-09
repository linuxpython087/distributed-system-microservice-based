from confluent_kafka import Consumer

c = Consumer({
    "bootstrap.servers": "kafka:9092",
    "group.id": "test-group",
    "auto.offset.reset": "earliest"
})

c.subscribe(["order_service_topics"])

while True:
    msg = c.poll(1.0)
    if msg is None:
        continue
    if msg.error():
        print(msg.error())
        continue

    print("RECEIVED:", msg.value().decode("utf-8"))