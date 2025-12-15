from __future__ import annotations

from abc import abstractmethod
from collections.abc import Generator

from fivcglue import IComponent


class IQueueProducer(IComponent):
    """Interface for a message queue producer."""

    @abstractmethod
    def produce(self, message: bytes) -> bool:
        """Send a message to the queue."""


class IQueueConsumer(IComponent):
    """Interface for a message queue consumer."""

    @abstractmethod
    def consume(self, **kwargs) -> Generator[bytes, None, None]:
        """Poll the queue for messages."""


class IQueueSite(IComponent):
    """Factory interface for creating and managing named queues."""

    @abstractmethod
    def get_producer(self, queue_name: str) -> IQueueProducer:
        """get a queue producer by name"""

    @abstractmethod
    def get_consumer(self, queue_name: str) -> IQueueConsumer:
        """get a queue consumer by name"""
