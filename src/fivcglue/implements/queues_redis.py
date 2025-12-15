"""Redis-based queue implementation using pub/sub.

This module provides a Redis-backed implementation of the queue interfaces.
It uses the redis-py library to connect to a Redis server and provides
distributed message queuing with pub/sub mechanism.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from fivcglue import IComponentSite, query_component
from fivcglue.interfaces import configs, queues

if TYPE_CHECKING:
    from collections.abc import Generator


class QueueProducerImpl(queues.IQueueProducer):
    """Redis-based queue producer implementation.

    Publishes messages to a Redis channel using the PUBLISH command.
    Messages are sent as bytes to the specified queue name (channel).

    Args:
        redis_client: Redis client instance (redis.Redis or compatible)
        queue_name: Name of the queue/channel to publish to

    Example:
        >>> producer = QueueProducerImpl(redis_client, "my_queue")
        >>> producer.produce(b"Hello, World!")
        True
    """

    def __init__(self, redis_client, queue_name: str):
        """Initialize a Redis queue producer.

        Args:
            redis_client: Redis client instance
            queue_name: Name of the queue/channel
        """
        self.redis_client = redis_client
        self.queue_name = queue_name

    def produce(self, message: bytes) -> bool:
        """Send a message to the queue.

        Uses Redis PUBLISH command to send the message to all subscribers
        of the queue channel.

        Args:
            message: Message to send as bytes

        Returns:
            bool: True if message was published, False on error
        """
        try:
            # PUBLISH returns the number of subscribers that received the message
            # We return True if publish succeeded (even if no subscribers)
            self.redis_client.publish(self.queue_name, message)
            return True
        except Exception as e:
            print(f"Warning: Failed to produce message to queue '{self.queue_name}': {e}")  # noqa
            return False


class QueueConsumerImpl(queues.IQueueConsumer):
    """Redis-based queue consumer implementation.

    Subscribes to a Redis channel using the SUBSCRIBE command and
    yields messages as they arrive.

    Args:
        redis_client: Redis client instance (redis.Redis or compatible)
        queue_name: Name of the queue/channel to subscribe to

    Example:
        >>> consumer = QueueConsumerImpl(redis_client, "my_queue")
        >>> for message in consumer.consume():
        ...     print(message)
    """

    def __init__(self, redis_client, queue_name: str):
        """Initialize a Redis queue consumer.

        Args:
            redis_client: Redis client instance
            queue_name: Name of the queue/channel to subscribe to
        """
        self.redis_client = redis_client
        self.queue_name = queue_name
        self.pubsub = None

    def consume(self, **kwargs) -> Generator[bytes, None, None]:
        """Poll the queue for messages.

        Subscribes to the queue channel and yields messages as they arrive.
        This is a blocking generator that will yield messages indefinitely
        until the subscription is closed.

        Args:
            **kwargs: Additional arguments (reserved for future use)

        Yields:
            bytes: Message data from the queue

        Example:
            >>> for message in consumer.consume():
            ...     print(f"Received: {message}")
        """
        try:
            # Create a pubsub object for this consumer
            self.pubsub = self.redis_client.pubsub()
            self.pubsub.subscribe(self.queue_name)

            # Iterate over messages from the subscription
            for message in self.pubsub.listen():
                # Filter out subscription confirmation messages
                if message["type"] == "message":
                    yield message["data"]

        except Exception as e:
            print(f"Warning: Error consuming from queue '{self.queue_name}': {e}")  # noqa
        finally:
            # Clean up subscription
            if self.pubsub:
                try:
                    self.pubsub.unsubscribe(self.queue_name)
                    self.pubsub.close()
                except Exception as e:
                    print(f"Warning: Error closing pubsub: {e}")  # noqa
                self.pubsub = None


class QueueSiteImpl(queues.IQueueSite):
    """Redis-based queue site for managing named queues.

    Provides a factory for creating QueueProducerImpl and QueueConsumerImpl
    instances that share the same Redis connection.

    Configuration is read from the IConfig component's "redis" session.
    If no config is available, defaults are used.

    Args:
        component_site: Component site instance (required by component system)
        **kwargs: Additional Redis client parameters

    Example:
        >>> site = ComponentSite()
        >>> queue_site = QueueSiteImpl(component_site=site)
        >>> producer = queue_site.get_producer("my_queue")
        >>> consumer = queue_site.get_consumer("my_queue")
    """

    def __init__(
        self,
        component_site: IComponentSite,
        **kwargs,
    ):
        """Initialize Redis queue site.

        Args:
            component_site: Component site instance (required by component system)
            **kwargs: Additional Redis client parameters
        """
        # Retrieve Redis configuration from IConfig component
        config = query_component(component_site, configs.IConfig)
        config = config and config.get_session("redis")
        if not config:
            raise RuntimeError("Config component not available")

        config_host = config.get_value("host") or "localhost"
        config_port = config.get_value("port") or 6379
        config_db = config.get_value("db") or 0
        config_password = config.get_value("password") or ""
        print(f"create queue site component of redis at {config_host}:{config_port}")  # noqa

        try:
            import redis

            # Create Redis client with retrieved configuration
            self.redis_client = redis.Redis(
                host=config_host,
                port=int(config_port),
                db=int(config_db),
                password=config_password,
                decode_responses=False,  # Keep binary mode for bytes compatibility
                socket_connect_timeout=5,  # 5 second connection timeout
                socket_timeout=5,  # 5 second operation timeout
                **kwargs,
            )

            # Test connection
            self.redis_client.ping()
            self.connected = True

        except ImportError:
            print("Warning: redis package not installed. Install with: pip install redis")  # noqa
            self.redis_client = None
            self.connected = False
        except Exception as e:
            print(f"Warning: Failed to connect to Redis at {config_host}:{config_port}: {e}")  # noqa
            self.redis_client = None
            self.connected = False

    def get_producer(self, queue_name: str) -> queues.IQueueProducer:
        """Get a queue producer by name.

        Creates a new QueueProducerImpl instance for the given queue name.
        Multiple calls with the same name will return different instances,
        but they will all publish to the same Redis channel.

        Args:
            queue_name: Name of the queue to produce to

        Returns:
            IQueueProducer instance if Redis is connected, None otherwise

        Raises:
            RuntimeError: If Redis is not connected
        """
        if not self.connected or self.redis_client is None:
            raise RuntimeError(
                f"Cannot create producer for queue '{queue_name}' - Redis not connected"
            )

        return cast(queues.IQueueProducer, QueueProducerImpl(self.redis_client, queue_name))

    def get_consumer(self, queue_name: str) -> queues.IQueueConsumer:
        """Get a queue consumer by name.

        Creates a new QueueConsumerImpl instance for the given queue name.
        Multiple calls with the same name will return different instances,
        but they will all subscribe to the same Redis channel.

        Args:
            queue_name: Name of the queue to consume from

        Returns:
            IQueueConsumer instance if Redis is connected, None otherwise

        Raises:
            RuntimeError: If Redis is not connected
        """
        if not self.connected or self.redis_client is None:
            raise RuntimeError(
                f"Cannot create consumer for queue '{queue_name}' - Redis not connected"
            )

        return cast(queues.IQueueConsumer, QueueConsumerImpl(self.redis_client, queue_name))
