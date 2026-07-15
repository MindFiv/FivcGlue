"""Redis-based queue implementation using pub/sub.

This module provides a Redis-backed implementation of the queue interfaces.
It uses redis.asyncio to connect to a Redis server and provides
distributed message queuing with pub/sub mechanism.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, cast

from fivcglue import IComponentSite, query_component
from fivcglue.interfaces import configs, queues

if TYPE_CHECKING:
    from datetime import timedelta


class QueueProducerImpl(queues.IQueueProducer):
    """Redis-based queue producer implementation.

    Publishes messages to a Redis channel using the PUBLISH command.
    Messages are sent as bytes to the specified queue name (channel).

    Args:
        redis_client: Async Redis client instance (redis.asyncio.Redis or compatible)
        queue_name: Name of the queue/channel to publish to

    Example:
        >>> producer = QueueProducerImpl(redis_client, "my_queue")
        >>> producer.produce(b"Hello, World!")
        True
    """

    def __init__(self, redis_client, queue_name: str):
        """Initialize a Redis queue producer.

        Args:
            redis_client: Async Redis client instance
            queue_name: Name of the queue/channel
        """
        self.redis_client = redis_client
        self.queue_name = queue_name

    def produce(self, message: bytes) -> bool:
        """Send a message to the queue (sync wrapper around produce_async)."""
        return asyncio.run(self.produce_async(message))

    async def produce_async(self, message: bytes) -> bool:
        """Send a message to the queue asynchronously.

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
            await self.redis_client.publish(self.queue_name, message)
            return True
        except Exception as e:
            print(f"Warning: Failed to produce message to queue '{self.queue_name}': {e}")  # noqa
            return False


class QueueConsumerImpl(queues.IQueueConsumer):
    """Redis-based queue consumer implementation.

    Subscribes to a Redis channel using the SUBSCRIBE command and
    returns messages one at a time.

    Args:
        redis_client: Async Redis client instance (redis.asyncio.Redis or compatible)
        queue_name: Name of the queue/channel to subscribe to

    Example:
        >>> consumer = QueueConsumerImpl(redis_client, "my_queue")
        >>> message = consumer.consume()
    """

    def __init__(self, redis_client, queue_name: str):
        """Initialize a Redis queue consumer.

        Args:
            redis_client: Async Redis client instance
            queue_name: Name of the queue/channel to subscribe to
        """
        self.redis_client = redis_client
        self.queue_name = queue_name
        self.pubsub = None

    def consume(self, timeout: timedelta | None = None, **kwargs) -> bytes | None:
        """Poll the queue for a single message (sync wrapper around consume_async)."""
        return asyncio.run(self.consume_async(timeout=timeout, **kwargs))

    async def consume_async(self, timeout: timedelta | None = None, **kwargs) -> bytes | None:
        """Poll the queue for a single message asynchronously.

        Args:
            timeout: Max wait duration. None means return immediately.
            **kwargs: Reserved for backward compatibility.

        Returns:
            Message bytes if available, otherwise None.
        """
        try:
            if self.pubsub is None:
                self.pubsub = self.redis_client.pubsub()
                await self.pubsub.subscribe(self.queue_name)

            redis_timeout = 0.0 if timeout is None else timeout.total_seconds()
            message = await self.pubsub.get_message(
                ignore_subscribe_messages=True,
                timeout=redis_timeout,
            )
            if message is None:
                return None
            return message["data"]
        except Exception as e:
            print(f"Warning: Error consuming from queue '{self.queue_name}': {e}")  # noqa
            return None


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
        config_username = config.get_value("username") or None
        config_password = config.get_value("password") or None
        print(f"create queue site component of redis at {config_host}:{config_port}")  # noqa

        try:
            import redis.asyncio as redis

            # Create async Redis client with retrieved configuration
            self.redis_client = redis.Redis(
                host=config_host,
                port=int(config_port),
                db=int(config_db),
                username=config_username,
                password=config_password,
                decode_responses=False,  # Keep binary mode for bytes compatibility
                socket_connect_timeout=5,  # 5 seconds connection timeout
                socket_timeout=5,  # 5 seconds operation timeout
                **kwargs,
            )

            # Test connection
            asyncio.run(self.redis_client.ping())
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
