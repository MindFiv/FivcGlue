# FivcGlue

A Domain-Driven Design (DDD) programming package for Python, similar to `zope.interface`.

## 🎯 Overview

FivcGlue provides a clean and intuitive way to implement Domain-Driven Design patterns in Python applications. It offers interfaces and implementations for common DDD building blocks, helping you structure your code following DDD principles.

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- UV package manager (recommended) or pip

### Installation

**With UV (recommended):**
```bash
# Install with development dependencies
make install

# Or minimal installation
make install-min

# With YAML support
uv sync --extra yaml
```

**With pip:**
```bash
# Basic installation
pip install -e .

# With YAML support
pip install -e ".[yaml]"

# With development dependencies
pip install -e ".[dev,yaml]"
```

## 📦 Features

FivcGlue provides core DDD building blocks:

- **Interfaces**: Define contracts for your domain components
- **Configurations**: Flexible configuration management (JSON, YAML)
- **Caching**: In-memory and Redis-based caching implementations
- **Logging**: Built-in logging utilities
- **Mutexes**: Distributed locking with Redis support

## 💻 Usage

### Basic Example

```python
from fivcglue.interfaces import IConfig
from fivcglue.implements import YAMLFileConfig

# Load configuration from YAML file
config = YAMLFileConfig("config.yml")
value = config.get("key", default="default_value")
```

### Configuration Management

```python
from fivcglue.implements import JSONFileConfig, YAMLFileConfig

# JSON configuration
json_config = JSONFileConfig("settings.json")

# YAML configuration (requires PyYAML)
yaml_config = YAMLFileConfig("settings.yml")
```

### Caching

```python
from datetime import timedelta
from fivcglue.implements.caches_mem import CacheImpl as MemoryCacheImpl
from fivcglue.implements.caches_redis import CacheImpl as RedisCacheImpl

# In-memory cache
cache = MemoryCacheImpl(_component_site=None, max_size=10000)
cache.set_value("key", b"value", expire=timedelta(hours=1))
value = cache.get_value("key")

# Redis cache (requires redis package)
redis_cache = RedisCacheImpl(_component_site=None, host="localhost", port=6379)
redis_cache.set_value("key", b"value", expire=timedelta(hours=1))
```

## 📁 Project Structure

```
src/fivcglue/
├── interfaces/      # Interface definitions
│   ├── configs.py   # Configuration interfaces
│   ├── caches.py    # Cache interfaces
│   ├── loggers.py   # Logger interfaces
│   └── mutexes.py   # Mutex interfaces
├── implements/      # Concrete implementations
│   ├── configs_jsonfile.py
│   ├── configs_yamlfile.py
│   ├── caches_mem.py
│   ├── caches_redis.py
│   ├── loggers_builtin.py
│   └── mutexes_redis.py
└── fixtures/        # Test fixtures
```

## 🛠️ Development

### Available Make Commands

```bash
make help        # Show all available commands
make install     # Install with dev dependencies
make install-min # Install minimal dependencies
make dev         # Install development dependencies
make lint        # Run code linting
make format      # Format code
make test        # Run tests
make test-cov    # Run tests with coverage
make clean       # Clean temporary files
make build       # Build distribution packages
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
uv run pytest tests/test_configs.py -v
```

### Code Quality

```bash
# Lint code
make lint

# Format code
make format
```

## 📚 Documentation

For more detailed documentation, see the [docs/](docs/) directory:

- [Architecture](docs/ARCHITECTURE.md) - System architecture and design
- [Dependencies](docs/DEPENDENCIES.md) - Dependency management guide

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

### Development Setup

1. Clone the repository
2. Install dependencies: `make install`
3. Run tests: `make test`
4. Format code: `make format`
5. Run linting: `make lint`

## 📄 License

MIT License - see LICENSE file for details

## 🔗 Links

- **Documentation**: [GitHub README](https://github.com/5C-Plus/fivcglue#readme)
- **Issues**: [GitHub Issues](https://github.com/5C-Plus/fivcglue/issues)
- **Source**: [GitHub Repository](https://github.com/5C-Plus/fivcglue)
