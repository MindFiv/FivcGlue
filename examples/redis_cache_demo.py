#!/usr/bin/env python3
"""Demonstration of Redis cache implementation.

This script demonstrates how to use the Redis cache implementation.
It requires a running Redis server (default: localhost:6379).

To run Redis locally using Docker:
    docker run -d -p 6379:6379 redis:latest

Or install Redis locally:
    # macOS
    brew install redis
    brew services start redis
    
    # Ubuntu/Debian
    sudo apt-get install redis-server
    sudo systemctl start redis
"""

from datetime import timedelta

from fivcglue.implements import ComponentSite
from fivcglue.implements.caches_redis import CacheImpl
from fivcglue.interfaces.caches import ICache


def main():
    """Demonstrate Redis cache usage."""
    print("=" * 60)
    print("Redis Cache Implementation Demo")
    print("=" * 60)
    print()

    # Create component site
    site = ComponentSite()

    # Create Redis cache with default settings (localhost:6379)
    print("Creating Redis cache (localhost:6379)...")
    cache = CacheImpl(_component_site=site)
    print()

    # Check if connected
    if not cache.connected:
        print("⚠️  Redis is not connected!")
        print("Please ensure Redis is running on localhost:6379")
        print()
        print("To start Redis with Docker:")
        print("  docker run -d -p 6379:6379 redis:latest")
        print()
        return

    print("✓ Connected to Redis successfully!")
    print()

    # Register cache with component site
    site.register_component(ICache, cache, name="redis")
    print("✓ Cache registered with component site")
    print()

    # Demonstrate basic operations
    print("-" * 60)
    print("Basic Cache Operations")
    print("-" * 60)
    print()

    # Set a value
    key = "demo:user:123"
    value = b'{"name": "John Doe", "email": "john@example.com"}'
    expire = timedelta(seconds=30)

    print(f"Setting key: {key}")
    print(f"Value: {value.decode()}")
    print(f"Expiration: {expire.total_seconds()} seconds")
    
    success = cache.set_value(key, value, expire)
    print(f"Result: {'✓ Success' if success else '✗ Failed'}")
    print()

    # Get the value back
    print(f"Getting key: {key}")
    retrieved = cache.get_value(key)
    
    if retrieved:
        print(f"Retrieved: {retrieved.decode()}")
        print("✓ Value found in cache")
    else:
        print("✗ Value not found")
    print()

    # Try to get a non-existent key
    print("Getting non-existent key: demo:nonexistent")
    result = cache.get_value("demo:nonexistent")
    print(f"Result: {result}")
    print("✓ Correctly returns None for missing keys")
    print()

    # Demonstrate expiration
    print("-" * 60)
    print("Expiration Demo")
    print("-" * 60)
    print()

    short_key = "demo:short_lived"
    short_value = b"This will expire in 2 seconds"
    short_expire = timedelta(seconds=2)

    print(f"Setting key with 2-second expiration: {short_key}")
    cache.set_value(short_key, short_value, short_expire)
    
    print("Immediately retrieving...")
    result = cache.get_value(short_key)
    print(f"Result: {result.decode() if result else 'None'}")
    print()

    print("Waiting 3 seconds for expiration...")
    import time
    time.sleep(3)
    
    print("Retrieving after expiration...")
    result = cache.get_value(short_key)
    print(f"Result: {result}")
    print("✓ Value correctly expired and removed by Redis")
    print()

    # Demonstrate updating a value
    print("-" * 60)
    print("Update Demo")
    print("-" * 60)
    print()

    update_key = "demo:counter"
    print(f"Setting initial value: {update_key} = 1")
    cache.set_value(update_key, b"1", timedelta(minutes=5))
    
    print(f"Updating value: {update_key} = 2")
    cache.set_value(update_key, b"2", timedelta(minutes=5))
    
    result = cache.get_value(update_key)
    print(f"Retrieved: {result.decode() if result else 'None'}")
    print("✓ Value successfully updated")
    print()

    # Demonstrate None value
    print("-" * 60)
    print("None Value Demo")
    print("-" * 60)
    print()

    none_key = "demo:none_value"
    print(f"Setting None value for key: {none_key}")
    cache.set_value(none_key, None, timedelta(minutes=1))
    
    result = cache.get_value(none_key)
    print(f"Retrieved: {result}")
    print(f"Type: {type(result)}")
    print("✓ None values are stored as empty bytes")
    print()

    # Clean up
    print("-" * 60)
    print("Cleanup")
    print("-" * 60)
    print()
    
    print("Cleaning up demo keys...")
    # Note: Redis will auto-expire these keys, but we could also delete them
    # if we had a delete method
    print("✓ Keys will auto-expire based on their TTL")
    print()

    print("=" * 60)
    print("Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

