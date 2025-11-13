# FivcGlue Architecture

This document describes the architecture and design principles of FivcGlue, a Domain-Driven Design (DDD) programming package for Python.

## 🎯 Design Philosophy

FivcGlue is designed following these core principles:

1. **Interface-Driven Design**: Clear separation between interfaces and implementations
2. **Domain-Driven Design**: Support for DDD patterns and building blocks
3. **Flexibility**: Multiple implementations for the same interface
4. **Simplicity**: Easy to use and understand
5. **Extensibility**: Easy to add new implementations

## 📁 Project Structure

```
src/fivcglue/
├── __init__.py          # Package initialization
├── __about__.py         # Version and metadata
├── interfaces/          # Interface definitions
│   ├── __init__.py
│   ├── configs.py       # Configuration interfaces
│   ├── caches.py        # Cache interfaces
│   ├── loggers.py       # Logger interfaces
│   ├── mutexes.py       # Mutex/lock interfaces
│   └── utils.py         # Utility interfaces
├── implements/          # Concrete implementations
│   ├── __init__.py
│   ├── configs_jsonfile.py    # JSON file config
│   ├── configs_yamlfile.py    # YAML file config
│   ├── caches_mem.py          # In-memory cache
│   ├── caches_redis.py        # Redis cache
│   ├── loggers_builtin.py     # Built-in logger
│   ├── mutexes_redis.py       # Redis mutex
│   └── utils.py               # Utility functions
└── fixtures/            # Test fixtures and examples
```

## 🏗️ Core Components

### 1. Interfaces Layer

The interfaces layer defines contracts for all components. This follows the **Dependency Inversion Principle** from SOLID.

**Key Interfaces:**

- **`IConfig`**: Configuration management interface
  - Methods: `get()`, `set()`, `has()`, `load()`, `save()`
  - Implementations: JSON, YAML

- **`ICache`**: Caching interface
  - Methods: `get()`, `set()`, `delete()`, `clear()`, `exists()`
  - Implementations: In-memory, Redis

- **`ILogger`**: Logging interface
  - Methods: `debug()`, `info()`, `warning()`, `error()`, `critical()`
  - Implementations: Built-in Python logging

- **`IMutex`**: Distributed locking interface
  - Methods: `acquire()`, `release()`, `is_locked()`
  - Implementations: Redis-based locks

### 2. Implementations Layer

Concrete implementations of the interfaces. Each implementation can be swapped without affecting client code.

**Configuration Implementations:**
- `ConfigImpl` (configs_jsonfile.py): File-based JSON configuration
- `ConfigImpl` (configs_yamlfile.py): File-based YAML configuration (requires PyYAML)

**Cache Implementations:**
- `CacheImpl` (caches_mem.py): Thread-safe in-memory cache with automatic expiration
- `CacheImpl` (caches_redis.py): Distributed cache using Redis

**Logger Implementations:**
- `LoggerImpl` (loggers_builtin.py): Wrapper around Python's built-in logging
- `LoggerSiteImpl` (loggers_builtin.py): Factory for creating logger instances

**Mutex Implementations:**
- `MutexImpl` (mutexes_redis.py): Distributed locks using Redis
- `MutexSiteImpl` (mutexes_redis.py): Factory for creating mutex instances



## 🔄 Design Patterns

### 1. Interface Segregation

Each interface is focused on a single responsibility:
- Configuration management
- Caching
- Logging
- Locking

### 2. Dependency Injection

Components depend on interfaces, not concrete implementations:

```python
# Good: Depend on interface
def process_data(cache: ICache, config: IConfig):
    value = config.get("key")
    cache.set("result", value)

# Usage with different implementations
from fivcglue.implements.caches_mem import CacheImpl as MemoryCacheImpl
from fivcglue.implements.caches_redis import CacheImpl as RedisCacheImpl
from fivcglue.implements.configs_jsonfile import ConfigImpl as JSONConfigImpl
from fivcglue.implements.configs_yamlfile import ConfigImpl as YAMLConfigImpl

process_data(MemoryCacheImpl(_component_site=None), JSONConfigImpl(_component_site=None, file_path="config.json"))
process_data(RedisCacheImpl(_component_site=None), YAMLConfigImpl(_component_site=None, file_path="config.yml"))
```

### 3. Factory Pattern

Create instances through factory functions or classes:

```python
from fivcglue.implements.caches_mem import CacheImpl as MemoryCacheImpl
from fivcglue.implements.caches_redis import CacheImpl as RedisCacheImpl

def create_cache(cache_type: str, **kwargs) -> ICache:
    if cache_type == "memory":
        return MemoryCacheImpl(_component_site=None, **kwargs)
    elif cache_type == "redis":
        return RedisCacheImpl(_component_site=None, **kwargs)
    raise ValueError(f"Unknown cache type: {cache_type}")
```

## 🧩 Extension Points

### Adding New Implementations

To add a new implementation:

1. **Define the interface** (if not exists):
```python
# src/fivcglue/interfaces/storage.py
class IStorage:
    def save(self, key: str, data: bytes) -> None:
        raise NotImplementedError

    def load(self, key: str) -> bytes:
        raise NotImplementedError
```

2. **Implement the interface**:
```python
# src/fivcglue/implements/storage_s3.py
from fivcglue.interfaces import IStorage

class S3Storage(IStorage):
    def __init__(self, bucket: str):
        self.bucket = bucket

    def save(self, key: str, data: bytes) -> None:
        # Implementation
        pass

    def load(self, key: str) -> bytes:
        # Implementation
        pass
```

3. **Export from package**:
```python
# src/fivcglue/implements/__init__.py
from .storage_s3 import S3Storage

__all__ = ["S3Storage"]
```

## 🎨 Best Practices

### 1. Always Program to Interfaces

```python
# Good
def process(cache: ICache):
    pass

# Avoid - don't depend on concrete implementations
from fivcglue.implements.caches_mem import CacheImpl
def process(cache: CacheImpl):  # Too specific!
    pass
```

### 2. Use Type Hints

```python
from typing import Optional
from fivcglue.interfaces import IConfig

def get_setting(config: IConfig, key: str) -> Optional[str]:
    return config.get(key)
```

### 3. Handle Errors Gracefully

```python
try:
    value = config.get("required_key")
except KeyError:
    # Handle missing configuration
    value = default_value
```

### 4. Keep Implementations Simple

Each implementation should focus on one thing and do it well.

## 🔍 Testing Strategy

### Unit Tests

Test each implementation independently:

```python
from datetime import timedelta
from fivcglue.implements.caches_mem import CacheImpl

def test_memory_cache():
    cache = CacheImpl(_component_site=None)
    cache.set_value("key", b"value", expire=timedelta(hours=1))
    assert cache.get_value("key") == b"value"
```

### Integration Tests

Test components working together:

```python
from fivcglue.implements.configs_jsonfile import ConfigImpl as JSONConfigImpl
from fivcglue.implements.caches_mem import CacheImpl

def test_config_with_cache():
    config = JSONConfigImpl(_component_site=None, file_path="test.json")
    cache = CacheImpl(_component_site=None)
    # Test integration
```

### Interface Compliance Tests

Ensure all implementations follow the interface contract:

```python
from fivcglue.implements.caches_mem import CacheImpl as MemoryCacheImpl
from fivcglue.implements.caches_redis import CacheImpl as RedisCacheImpl

def test_cache_interface_compliance():
    for cache_impl in [MemoryCacheImpl(_component_site=None), RedisCacheImpl(_component_site=None)]:
        assert hasattr(cache_impl, "get_value")
        assert hasattr(cache_impl, "set_value")
        # Test interface methods
```

## 📚 Further Reading

- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [zope.interface Documentation](https://zopeinterface.readthedocs.io/)

