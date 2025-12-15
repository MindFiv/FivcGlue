"""Redis-based cache implementation.

This module provides a Redis-backed implementation of the ICache interface.
It uses the redis-py library to connect to a Redis server and provides
distributed caching with automatic expiration support.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fivcglue import IComponentSite, query_component
from fivcglue.interfaces import caches, configs

if TYPE_CHECKING:
    from datetime import timedelta


class CacheImpl(caches.ICache):
    """Redis-based distributed cache implementation.

    Provides a distributed cache using Redis as the backend storage.
    All cached values are stored with expiration times and are automatically
    removed by Redis when they expire.

    This implementation is suitable for distributed systems where multiple
    processes or servers need to share cached data.

    Configuration is read from the IConfig component's "redis" session.
    If no config is available, defaults are used.

    Args:
        component_site: Component site instance (required by component system).
        **kwargs: Additional Redis client parameters.

    Example:
        >>> site = ComponentSite()
        >>> cache = CacheImpl(component_site=site)
        >>> from datetime import timedelta
        >>> cache.set_value("user:123", b"John Doe", expire=timedelta(hours=1))
        True
        >>> cache.get_value("user:123")
        b'John Doe'
    """

    def __init__(
        self,
        component_site: IComponentSite,
        **kwargs,
    ):
        """Initialize Redis cache connection.

        Establishes a connection to the Redis server with configuration
        read from the IConfig component. If the connection fails or the
        redis library is not installed, the cache will be in a disconnected
        state and all operations will fail gracefully.

        Args:
            component_site: Component site instance (required by component system).
            **kwargs: Additional Redis client parameters such as:
                - socket_connect_timeout: Connection timeout in seconds
                - socket_timeout: Operation timeout in seconds
                - max_connections: Maximum number of connections in the pool
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
        print(f"create cache of redis at {config_host}:{config_port}")  # noqa

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

    def get_value(
        self,
        key_name: str,
    ) -> bytes | None:
        """Retrieve a value from Redis cache by key name.

        Uses Redis GET command to retrieve the cached value. Redis automatically
        handles expiration, so expired keys will return None.

        Args:
            key_name: The cache key to retrieve.

        Returns:
            The cached value as bytes if found and not expired, None otherwise.
            Also returns None if Redis is not connected or an error occurs.

        Example:
            >>> value = cache.get_value("user:123")
            >>> if value:
            ...     print(f"Found: {value.decode()}")
            ... else:
            ...     print("Not found or expired")
        """
        if not self.connected or self.redis_client is None:
            return None

        try:
            # Redis GET returns None if key doesn't exist or has expired
            value = self.redis_client.get(key_name)
            return value  # Already bytes or None
        except Exception as e:
            # Log error in production; for now, print and return None
            print(f"Error getting cache value for key '{key_name}': {e}")  # noqa
            return None

    def set_value(
        self,
        key_name: str,
        value: bytes | None,
        expire: timedelta,
    ) -> bool:
        """Store a value in Redis cache with an expiration time.

        Uses Redis SETEX command to atomically set a value with an expiration time.
        Redis will automatically remove the key after the expiration time has elapsed.

        Args:
            key_name: The cache key to store the value under.
            value: The value to cache as bytes, or None to cache a null value.
            expire: Time duration until the cached value expires.
                Must be a positive timedelta.

        Returns:
            True if the value was successfully cached, False otherwise.
            Returns False if Redis is not connected or an error occurs.

        Example:
            >>> from datetime import timedelta
            >>> success = cache.set_value(
            ...     "session:abc123",
            ...     b'{"user_id": 42}',
            ...     expire=timedelta(minutes=30)
            ... )
            >>> if success:
            ...     print("Value cached successfully")
        """
        if not self.connected or self.redis_client is None:
            print(f"Warning: Cannot set cache value for '{key_name}' - Redis not connected")  # noqa
            return False

        try:
            # Convert timedelta to seconds (Redis SETEX expects integer seconds)
            expire_seconds = int(expire.total_seconds())

            # Ensure expiration time is positive
            if expire_seconds <= 0:
                print(
                    f"Warning: Invalid expiration time for key '{key_name}': {expire_seconds} seconds"
                )  # noqa
                return False

            # Use SETEX to atomically set value with expiration
            # SETEX key seconds value
            # Returns True on success
            result = self.redis_client.setex(
                key_name,
                expire_seconds,
                value if value is not None else b"",  # Store empty bytes for None
            )

            return bool(result)

        except Exception as e:
            # Log error in production; for now, print and return False
            print(f"Error setting cache value for key '{key_name}': {e}")  # noqa
            return False
