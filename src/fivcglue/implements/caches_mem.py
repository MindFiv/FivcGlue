from __future__ import annotations

import threading
import time
from typing import TYPE_CHECKING

from fivcglue import IComponentSite
from fivcglue.interfaces import caches

if TYPE_CHECKING:
    from datetime import timedelta


class CacheImpl(caches.ICache):
    """
    Thread-safe in-memory cache implementation with automatic expiration.

    Stores key-value pairs in memory with expiration times. Expired entries
    are automatically cleaned up when accessed or during set operations.
    """

    def __init__(
        self,
        _component_site: IComponentSite,
        max_size: int = 10000,
        cleanup_interval: int = 100,
        **_kwargs,
    ):
        """
        Initialize in-memory cache.

        Args:
            _component_site: Component site instance (required by component system)
            max_size: Maximum number of entries to store (default: 10000)
            cleanup_interval: Number of operations between cleanup runs (default: 100)
            **_kwargs: Additional parameters (ignored)
        """
        print("create cache of memory")  # noqa

        # Storage: {key: (value, expiration_timestamp)}
        self._cache: dict[str, tuple[bytes | None, float]] = {}

        # Thread safety lock
        self._lock = threading.Lock()

        # Configuration
        self._max_size = max_size
        self._cleanup_interval = cleanup_interval
        self._operation_count = 0

    def get_value(self, key_name: str) -> bytes | None:
        """
        Get value by key name.

        Automatically removes the entry if it has expired.

        Args:
            key_name: The cache key to retrieve

        Returns:
            bytes | None: The cached value if found and not expired, None otherwise
        """
        with self._lock:
            # Check if key exists
            if key_name not in self._cache:
                return None

            value, expiration_time = self._cache[key_name]
            current_time = time.time()

            # Check if expired
            if current_time >= expiration_time:
                # Remove expired entry
                del self._cache[key_name]
                return None

            return value

    def set_value(
        self,
        key_name: str,
        value: bytes | None,
        expire: timedelta,
    ) -> bool:
        """
        Set value with expiration time.

        Stores the value in memory with an expiration timestamp.
        Performs periodic cleanup of expired entries.

        Args:
            key_name: The cache key to set
            value: The value to cache (bytes or None)
            expire: Time until expiration (timedelta)

        Returns:
            bool: True if value was set successfully, False otherwise
        """
        try:
            with self._lock:
                # Calculate expiration timestamp
                expiration_time = time.time() + expire.total_seconds()

                # Check if we need to make room (if at max capacity and key is new)
                if len(self._cache) >= self._max_size and key_name not in self._cache:
                    # Try to clean up expired entries first
                    self._cleanup_expired()

                    # If still at capacity, remove oldest entry (FIFO)
                    if len(self._cache) >= self._max_size:
                        # Remove first key (oldest in insertion order for Python 3.7+)
                        first_key = next(iter(self._cache))
                        del self._cache[first_key]

                # Store value with expiration time
                self._cache[key_name] = (value, expiration_time)

                # Increment operation counter and check if cleanup is needed
                self._operation_count += 1
                if self._operation_count >= self._cleanup_interval:
                    self._cleanup_expired()
                    self._operation_count = 0

                return True

        except Exception as e:
            # Log error in production; for now, print and return False
            print(f"Error setting cache value for key '{key_name}': {e}")  # noqa
            return False

    def _cleanup_expired(self) -> None:
        """
        Remove all expired entries from the cache.

        This method should be called while holding the lock.
        """
        current_time = time.time()
        expired_keys = [
            key
            for key, (_, expiration_time) in self._cache.items()
            if current_time >= expiration_time
        ]

        for key in expired_keys:
            del self._cache[key]
