import json
import logging
import os
from threading import Lock

from kafka import KafkaProducer
from kafka.errors import KafkaError


logger = logging.getLogger(__name__)


class KafkaEventProducer:
    """
    Thread-safe KafkaProducer singleton with send_event method.
    """

    _instance = None
    _lock = Lock()

    @classmethod
    def _get_instance(cls) -> KafkaProducer:
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    bootstrap_servers = os.getenv(
                        "KAFKA_BOOTSTRAP_SERVERS", "kafka-broker:9092"
                    )
                    logger.info(
                        "Initializing KafkaProducer with bootstrap_servers=%s",
                        bootstrap_servers,
                    )

                    try:
                        cls._instance = KafkaProducer(
                            bootstrap_servers=bootstrap_servers,
                            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                            retries=5,
                            linger_ms=10,
                        )
                        logger.info("KafkaProducer initialized successfully")
                    except KafkaError as e:
                        logger.exception("Failed to initialize KafkaProducer")
                        raise e
        return cls._instance

    @classmethod
    def send_event(cls, topic: str, payload: dict) -> None:
        """
        Sends an event to the specified Kafka topic.
        """
        producer = cls._get_instance()
        try:
            producer.send(topic, value=payload)
            producer.flush()
            logger.info("Kafka event sent to '%s': %s", topic, payload)
        except KafkaError:
            logger.exception("Failed to send Kafka event")
