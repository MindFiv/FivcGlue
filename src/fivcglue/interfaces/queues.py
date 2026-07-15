from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from fivcglue import IComponent

if TYPE_CHECKING:
    from datetime import timedelta


class IQueueProducer(IComponent):
    """Interface for a message queue producer."""

    @abstractmethod
    def produce(self, message: bytes) -> bool:
        """Send a message to the queue."""

    @abstractmethod
    async def produce_async(self, message: bytes) -> bool:
        """Async variant of produce."""


class IQueueConsumer(IComponent):
    """Interface for a message queue consumer."""

    @abstractmethod
    def consume(self, timeout: timedelta | None = None, **kwargs) -> bytes | None:
        """Poll the queue for a single message.

        Args:
            timeout: Max wait duration. None means return immediately.
            **kwargs: Reserved for backward compatibility.

        Returns:
            Message bytes if available, otherwise None.
        """

    @abstractmethod
    async def consume_async(self, timeout: timedelta | None = None, **kwargs) -> bytes | None:
        """Async variant of consume.

        Args:
            timeout: Max wait duration. None means return immediately.
            **kwargs: Reserved for backward compatibility.

        Returns:
            Message bytes if available, otherwise None.
        """


class IQueueSite(IComponent):
    """Factory interface for creating and managing named queues."""

    @abstractmethod
    def get_producer(self, queue_name: str) -> IQueueProducer:
        """get a queue producer by name"""

    @abstractmethod
    def get_consumer(self, queue_name: str) -> IQueueConsumer:
        """get a queue consumer by name"""
