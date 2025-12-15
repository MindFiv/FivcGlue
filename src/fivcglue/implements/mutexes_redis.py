from __future__ import annotations

from typing import TYPE_CHECKING, cast

from fivcglue import IComponentSite, query_component
from fivcglue.interfaces import configs, mutexes

if TYPE_CHECKING:
    from datetime import timedelta


class MutexImpl(mutexes.IMutex):
    """
    Redis-based distributed mutex implementation.

    Uses Redis SET command with NX (not exists) and EX (expiration) options
    to implement a distributed lock mechanism.
    """

    def __init__(self, redis_client, mutex_name: str):
        """
        Initialize a Redis mutex.

        Args:
            redis_client: Redis client instance (redis.Redis or compatible)
            mutex_name: Unique name for this mutex
        """
        self.redis_client = redis_client
        self.mutex_name = mutex_name
        self.lock_key = f"mutex:{mutex_name}"
        self.lock_value = f"locked_by_{id(self)}"  # Unique identifier for this lock instance

    def acquire(
        self,
        expire: timedelta,
        method: str = "blocking",
    ) -> bool:
        """
        Acquire the mutex lock.

        Args:
            expire: Lock expiration time (timedelta)
            method: Acquisition method - "blocking" or "non-blocking"
                   Note: Current implementation treats both as non-blocking

        Returns:
            bool: True if lock was acquired, False otherwise
        """
        try:
            # Use Redis SET with NX (only set if not exists) and EX (expiration in seconds)
            # This is an atomic operation that ensures only one client can acquire the lock
            expire_seconds = int(expire.total_seconds())

            # SET key value NX EX seconds
            # Returns True if key was set, False if key already exists
            result = self.redis_client.set(
                self.lock_key,
                self.lock_value,
                nx=True,  # Only set if key doesn't exist
                ex=expire_seconds,  # Set expiration time
            )

            return bool(result)
        except Exception as e:
            # Log error in production; for now, print and return False
            print(f"Error acquiring mutex {self.mutex_name}: {e}")  # noqa
            return False

    def release(self) -> bool:
        """
        Release the mutex lock.

        Only releases the lock if it was acquired by this instance
        (verified by checking the lock value).

        Returns:
            bool: True if lock was released, False otherwise
        """
        try:
            # Use Lua script to atomically check and delete the lock
            # This ensures we only delete our own lock
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """

            result = self.redis_client.eval(
                lua_script,
                1,  # Number of keys
                self.lock_key,  # KEYS[1]
                self.lock_value,  # ARGV[1]
            )

            return bool(result)
        except Exception as e:
            # Log error in production; for now, print and return False
            print(f"Error releasing mutex {self.mutex_name}: {e}")  # noqa
            return False


class MutexSiteImpl(mutexes.IMutexSite):
    """
    Redis-based mutex site for managing distributed mutexes.

    Provides a factory for creating MutexImpl instances that share
    the same Redis connection.

    Configuration is read from the IConfig component's "redis" session.
    If no config is available, defaults are used.
    """

    def __init__(
        self,
        component_site: IComponentSite,
        **kwargs,
    ):
        """
        Initialize Redis mutex site.

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
        print(f"create mutex site component of redis at {config_host}:{config_port}")  # noqa

        try:
            import redis

            # Create Redis client with retrieved configuration
            self.redis_client = redis.Redis(
                host=config_host,
                port=int(config_port),
                db=int(config_db),
                password=config_password,
                decode_responses=False,  # Keep binary mode for compatibility
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

    def get_mutex(self, mtx_name: str) -> mutexes.IMutex | None:
        """
        Get a mutex by name.

        Creates a new MutexImpl instance for the given name.
        Multiple calls with the same name will return different instances,
        but they will all reference the same distributed lock in Redis.

        Args:
            mtx_name: Name of the mutex to retrieve

        Returns:
            IMutex instance if Redis is connected, None otherwise
        """
        if not self.connected or self.redis_client is None:
            print(f"Warning: Cannot create mutex '{mtx_name}' - Redis not connected")  # noqa
            return None

        # MutexImpl inherits from IMutex, so it's already compatible
        # Use cast() to inform type checkers about the return type
        return cast(mutexes.IMutex, MutexImpl(self.redis_client, mtx_name))
