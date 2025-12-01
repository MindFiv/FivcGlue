"""FivcGlue - A lightweight dependency injection framework for Python.

FivcGlue provides a component-based architecture with dependency injection
capabilities. It allows you to:

- Define component interfaces using abstract base classes
- Register component implementations with a central component site
- Query and retrieve components by interface type and optional name
- Load component configurations from JSON or YAML files
- Organize components into logical groups (caches, configs, loggers, mutexes)

The framework follows a service locator pattern where components are registered
with a component site and can be retrieved later using their interface type.

Core Interfaces:
    - IComponent: Base interface for all components
    - IComponentSite: Registry for managing component instances
    - IComponentSiteBuilder: Builder for loading component configurations
    - utils: Utility functions for component management

Example:
    >>> from fivcglue import IComponentSite
    >>> from fivcglue.implements import ComponentSite
    >>> from fivcglue.interfaces.caches import ICache
    >>> from fivcglue.implements.caches_mem import CacheImpl
    >>>
    >>> # Create component site and register a cache
    >>> site = ComponentSite()
    >>> cache = CacheImpl(_component_site=site)
    >>> site.register_component(ICache, cache, name="default")
    >>>
    >>> # Retrieve and use the cache
    >>> retrieved_cache = site.get_component(ICache, name="default")
    >>> from datetime import timedelta
    >>> retrieved_cache.set_value("key", b"value", expire=timedelta(hours=1))
"""

__all__ = [
    "__version__",
    "IComponent",
    "IComponentSite",
    "IComponentSiteBuilder",
    "utils",
    "cast_component",
    "query_component",
    "LazyValue",
]

from .__about__ import __version__  # noqa
from .interfaces import (  # noqa
    IComponent,
    IComponentSite,
    IComponentSiteBuilder,
    utils,
)
from .interfaces.utils import (
    cast_component,
    query_component,
)
from .lazy import LazyValue
