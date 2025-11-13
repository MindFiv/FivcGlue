# Redis Cache Implementation

## Overview

The Redis cache implementation (`src/fivcglue/implements/caches_redis.py`) provides a production-ready, distributed caching solution using Redis as the backend storage. This implementation is suitable for distributed systems where multiple processes or servers need to share cached data.

## Features

### ✅ Completed Implementation

1. **Full Redis Integration**
   - Uses `redis-py` library for Redis connectivity
   - Configurable connection parameters (host, port, db, password)
   - Connection pooling and timeout configuration
   - Automatic connection testing on initialization

2. **Robust Error Handling**
   - Graceful handling of missing `redis` library (ImportError)
   - Connection failure handling with warning messages
   - Operation-level error handling for get/set operations
   - Disconnected state management

3. **Complete ICache Interface Implementation**
   - `get_value()`: Retrieves cached values using Redis GET
   - `set_value()`: Stores values with expiration using Redis SETEX
   - Automatic expiration handled by Redis
   - Binary data support (bytes)

4. **Production-Ready Features**
   - Connection timeouts (5 seconds default)
   - Binary mode for bytes compatibility
   - Atomic operations (SETEX)
   - Proper expiration time validation
   - Comprehensive error logging

5. **Comprehensive Documentation**
   - Module-level docstring
   - Class-level docstring with examples
   - Method-level docstrings with Args/Returns/Examples
   - Google-style docstring format

## Usage

### Basic Usage

```python
from datetime import timedelta
from fivcglue.implements import ComponentSite
from fivcglue.implements.caches_redis import CacheImpl
from fivcglue.interfaces.caches import ICache

# Create component site
site = ComponentSite()

# Create Redis cache with default settings
cache = CacheImpl(_component_site=site)

# Or with custom settings
cache = CacheImpl(
    _component_site=site,
    host="redis.example.com",
    port=6379,
    db=0,
    password="secret"
)

# Register with component site
site.register_component(ICache, cache, name="redis")

# Store a value
cache.set_value(
    "user:123",
    b'{"name": "John Doe"}',
    expire=timedelta(hours=1)
)

# Retrieve a value
value = cache.get_value("user:123")
if value:
    print(f"Found: {value.decode()}")
```

### Configuration Parameters

The `CacheImpl` constructor accepts the following parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `_component_site` | `IComponentSite` | Required | Component site instance |
| `host` | `str` | `"localhost"` | Redis server hostname |
| `port` | `int` | `6379` | Redis server port |
| `db` | `int` | `0` | Redis database number |
| `password` | `str \| None` | `None` | Redis authentication password |
| `**kwargs` | `dict` | `{}` | Additional redis-py parameters |

Additional `**kwargs` can include:
- `socket_connect_timeout`: Connection timeout in seconds
- `socket_timeout`: Operation timeout in seconds
- `max_connections`: Maximum connections in the pool
- Any other `redis.Redis` parameters

### Using with Component Site Builder

The Redis cache can be configured via YAML/JSON configuration files:

```yaml
- entries:
    - interface: fivcglue.interfaces.caches.ICache
      name: 'Redis'
  
  class: fivcglue.implements.caches_redis.CacheImpl
  host: localhost
  port: 6379
  db: 0
```

Then load it:

```python
from fivcglue.implements.utils import load_component_site

site = load_component_site("config.yml", fmt="yml")
cache = site.get_component(ICache, name="Redis")
```

## Implementation Details

### Connection Management

The implementation establishes a Redis connection during initialization:

1. Imports the `redis` library (handles ImportError gracefully)
2. Creates a `redis.Redis` client with provided configuration
3. Tests the connection with `PING` command
4. Sets `self.connected` flag based on success/failure

If connection fails, the cache enters a disconnected state where:
- `get_value()` returns `None`
- `set_value()` returns `False`
- Warning messages are printed

### Data Storage

- **Keys**: Stored as-is (strings)
- **Values**: Stored as bytes (binary mode)
- **Expiration**: Handled automatically by Redis using SETEX
- **None values**: Stored as empty bytes (`b""`)

### Redis Commands Used

1. **SETEX** (Set with Expiration)
   - Atomically sets a key with an expiration time
   - Syntax: `SETEX key seconds value`
   - Used in `set_value()` method

2. **GET** (Get Value)
   - Retrieves the value of a key
   - Returns `None` if key doesn't exist or has expired
   - Used in `get_value()` method

3. **PING** (Test Connection)
   - Tests if the Redis server is responsive
   - Used during initialization

### Error Handling

The implementation handles several error scenarios:

1. **Missing redis library**: Prints warning, sets `connected = False`
2. **Connection failure**: Prints warning with details, sets `connected = False`
3. **Operation errors**: Prints error message, returns None/False
4. **Invalid expiration**: Validates positive expiration time

## Comparison with Memory Cache

| Feature | Redis Cache | Memory Cache |
|---------|-------------|--------------|
| **Storage** | External Redis server | In-process memory |
| **Persistence** | Survives process restart | Lost on restart |
| **Distribution** | Shared across processes | Process-local |
| **Capacity** | Redis server memory | Configurable max_size |
| **Expiration** | Redis automatic | Manual cleanup |
| **Thread Safety** | Redis handles it | Manual locking |
| **Performance** | Network latency | In-memory speed |

## Testing

The implementation passes all existing tests:

```bash
make test
# All 63 tests pass
```

The test in `tests/test_caches.py` verifies:
- Cache can be instantiated from configuration
- `get_value()` method can be called without errors

## Demo Script

A comprehensive demonstration script is available at `examples/redis_cache_demo.py`:

```bash
# Ensure Redis is running
docker run -d -p 6379:6379 redis:latest

# Run the demo
python examples/redis_cache_demo.py
```

The demo shows:
- Basic set/get operations
- Expiration behavior
- Updating values
- Handling None values
- Error handling

## Dependencies

The Redis cache requires the `redis` library:

```bash
pip install redis
```

Or add to your `pyproject.toml`:

```toml
[project.optional-dependencies]
redis = ["redis>=4.0.0"]
```

## Best Practices

1. **Always set expiration times**: Prevents unbounded cache growth
2. **Handle connection failures**: Check `cache.connected` if needed
3. **Use appropriate timeouts**: Configure based on your network
4. **Monitor Redis memory**: Set `maxmemory` policy in Redis config
5. **Use connection pooling**: Enabled by default in redis-py
6. **Serialize complex data**: Convert to bytes before caching

## Future Enhancements

Potential improvements for future versions:

1. **Delete method**: Add ability to manually delete keys
2. **Batch operations**: Support MGET/MSET for multiple keys
3. **Key patterns**: Support for listing/deleting by pattern
4. **TTL inspection**: Method to check remaining expiration time
5. **Metrics**: Track hit/miss rates, operation counts
6. **Retry logic**: Automatic retry on transient failures
7. **Sentinel support**: High availability with Redis Sentinel
8. **Cluster support**: Redis Cluster for horizontal scaling

## Troubleshooting

### Redis not connected

**Symptom**: Warning message "Failed to connect to Redis"

**Solutions**:
- Ensure Redis server is running
- Check host/port configuration
- Verify network connectivity
- Check firewall rules
- Verify Redis authentication (password)

### Import error

**Symptom**: Warning message "redis package not installed"

**Solution**:
```bash
pip install redis
```

### Values not persisting

**Symptom**: Values disappear immediately

**Possible causes**:
- Expiration time too short
- Redis maxmemory policy evicting keys
- Redis server restarted without persistence

### Performance issues

**Symptom**: Slow cache operations

**Solutions**:
- Check network latency to Redis server
- Increase timeout values
- Use connection pooling (enabled by default)
- Consider Redis pipelining for batch operations
- Monitor Redis server performance

## License

This implementation is part of the FivcGlue project and follows the same license.

