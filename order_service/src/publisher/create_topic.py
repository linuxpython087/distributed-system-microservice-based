

from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import KafkaException
import sys

def create_kafka_topic(bootstrap_servers, topic_name, num_partitions=1, replication_factor=1, config=None):
    """
    Create a Kafka topic using Confluent's AdminClient.

    :param bootstrap_servers: Kafka bootstrap servers (e.g., "localhost:9092")
    :param topic_name: Name of the topic to create
    :param num_partitions: Number of partitions
    :param replication_factor: Replication factor
    :param config: Optional dict of topic-level configurations
    """
    try:
        admin_client = AdminClient({"bootstrap.servers": bootstrap_servers})

        # Check if topic already exists
        cluster_metadata = admin_client.list_topics(timeout=5)
        print(cluster_metadata.topics)
        if topic_name in cluster_metadata.topics:
            print(f"Topic '{topic_name}' already exists.")
            return
        


        # Create topic object
        new_topic = NewTopic(
            topic=topic_name,
            num_partitions=num_partitions,
            replication_factor=replication_factor,
            config=config or {}
        )


        # Send create request
        futures = admin_client.create_topics([new_topic])

        # Wait for result
        for topic, future in futures.items():
            try:
                future.result()  # Raises exception if creation failed
                print(f"Topic '{topic}' created successfully.")
            except KafkaException as e:
                print(f"Failed to create topic '{topic}': {e}")
            except Exception as e:
                print(f"Unexpected error creating topic '{topic}': {e}")

    except Exception as e:
        print(f"Error connecting to Kafka: {e}")
        sys.exit(1)




if __name__ == "__main__":
    # Example usage
    create_kafka_topic(
        bootstrap_servers="kafka:9092",
        topic_name="order_service_topics",
        num_partitions=3,
        replication_factor=1,
        config={
            "cleanup.policy": "delete",  # or "compact"
            "retention.ms": "604800000"  # 7 days
        }
    )
