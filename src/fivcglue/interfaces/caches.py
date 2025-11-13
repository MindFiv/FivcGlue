"""Cache interface for key-value storage with expiration support.

This module defines the ICache interface for implementing cache services.
Cache implementations can be in-memory, Redis-based, or any other storage backend.
All cached values must have an expiration time to prevent unbounded growth.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from fivcglue import IComponent

if TYPE_CHECKING:
    from datetime import timedelta


class ICache(IComponent):
    """Interface for cache services with key-value storage and expiration.

    ICache provides a simple key-value storage interface where all values
    must have an expiration time. Values are stored as bytes to support
    any serializable data type.

    Implementations should:
    - Support automatic expiration of cached values
    - Handle concurrent access safely (if applicable)
    - Return None for missing or expired keys

    Example:
        >>> from datetime import timedelta
        >>> cache = MemoryCacheImpl(_component_site=None)
        >>> cache.set_value("user:123", b"John Doe", expire=timedelta(hours=1))
        True
        >>> cache.get_value("user:123")
        b'John Doe'
    """

    @abstractmethod
    def get_value(
        self,
        key_name: str,
    ) -> bytes | None:
        """Retrieve a value from the cache by key name.

        Returns the cached value if it exists and has not expired.
        Expired entries should be automatically removed when accessed.

        Args:
            key_name: The cache key to retrieve.

        Returns:
            The cached value as bytes if found and not expired, None otherwise.
        """

    @abstractmethod
    def set_value(
        self,
        key_name: str,
        value: bytes | None,
        expire: timedelta,
    ) -> bool:
        """Store a value in the cache with an expiration time.

        All cached values must have an expiration time to prevent unbounded
        cache growth. The value will be automatically removed after the
        expiration time has elapsed.

        Args:
            key_name: The cache key to store the value under.
            value: The value to cache as bytes, or None to cache a null value.
            expire: Time duration until the cached value expires.
                Must be a positive timedelta.

        Returns:
            True if the value was successfully cached, False otherwise.
        """
