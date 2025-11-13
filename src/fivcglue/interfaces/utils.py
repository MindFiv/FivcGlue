"""Utility functions for component management and dynamic imports.

This module provides helper functions for working with components:
- cast_component: Type-safe casting of component instances
- query_component: Convenience wrapper for querying components with type casting
- implements: Decorator for marking classes as component implementations (DEPRECATED)
- import_string: Dynamic import of classes from dotted module paths

Note:
    The @implements decorator is deprecated. Use direct inheritance instead:
    ``class MyImpl(IInterface):`` provides better IDE support, type checking,
    and follows standard Python conventions.
"""

from __future__ import annotations

import warnings
from collections.abc import Callable
from importlib import import_module
from typing import (
    Any,
    TypeVar,
)

from . import IComponent, IComponentSite  # noqa

_Int = TypeVar("_Int")  # interface class
_Imp = TypeVar("_Imp")  # implement class


def cast_component(
    instance: Any,
    instance_type: type[_Int],
) -> _Int | None:
    """Cast an instance to a specific component type if compatible.

    Performs a type check and returns the instance cast to the target type
    if it's an instance of that type, otherwise returns None.

    Args:
        instance: The instance to cast.
        instance_type: The target type to cast to.

    Returns:
        The instance cast to instance_type if compatible, None otherwise.

    Example:
        >>> component = get_some_component()
        >>> cache = cast_component(component, ICache)
        >>> if cache:
        ...     cache.get_value("key")
    """
    return instance if isinstance(instance, instance_type) else None


def query_component(
    interface_site: IComponentSite,
    interface_type: type[_Int],
    name: str = "",
) -> _Int | None:
    """Query a component from the site with automatic type casting.

    Convenience wrapper around IComponentSite.query_component that performs
    type casting to the requested interface type.

    Args:
        interface_site: The component site to query.
        interface_type: The interface type to look up.
        name: Optional name to distinguish between multiple implementations.
            Defaults to empty string.

    Returns:
        The component instance cast to the interface type if found, None otherwise.

    Example:
        >>> from fivcglue.interfaces import caches
        >>> cache = query_component(site, caches.ICache, name="Redis")
        >>> if cache:
        ...     cache.set_value("key", b"value", expire=timedelta(hours=1))
    """
    i = interface_site.query_component(interface_type, name=name)
    return cast_component(i, interface_type) if i else None


def implements(interfaces: type[_Int] | list[type[_Int]]) -> Callable[[type[_Imp]], type[_Imp]]:
    """Decorator to mark a class as implementing one or more component interfaces.

    .. deprecated::
        The @implements decorator is deprecated. Use direct inheritance instead:
        ``class MyImpl(IInterface):`` instead of ``@implements(IInterface) class MyImpl:``.
        This provides better IDE support, type checking, and follows standard Python conventions.

    This decorator creates a wrapper class that inherits from both the original
    class and the specified interface(s). This ensures that the class properly
    implements the interface contract and can be used with isinstance checks.

    Args:
        interfaces: A single interface class or list of interface classes that
            the decorated class implements. All interfaces must inherit from
            IComponent.

    Returns:
        A decorator function that wraps the class with the interface inheritance.

    Raises:
        TypeError: If any of the provided interfaces do not inherit from IComponent.

    Example (deprecated):
        >>> @implements(ICache)
        ... class MemoryCacheImpl:
        ...     def get_value(self, key_name: str) -> bytes | None:
        ...         return self._cache.get(key_name)
        ...     def set_value(self, key_name: str, value: bytes | None, expire: timedelta) -> bool:
        ...         self._cache[key_name] = value
        ...         return True

    Recommended approach:
        >>> class MemoryCacheImpl(ICache):
        ...     def get_value(self, key_name: str) -> bytes | None:
        ...         return self._cache.get(key_name)
        ...     def set_value(self, key_name: str, value: bytes | None, expire: timedelta) -> bool:
        ...         self._cache[key_name] = value
        ...         return True
    """
    warnings.warn(
        "The @implements decorator is deprecated. Use direct inheritance instead: "
        "class MyImpl(IInterface): instead of @implements(IInterface) class MyImpl:. "
        "Direct inheritance provides better IDE support, type checking, and follows "
        "standard Python conventions.",
        DeprecationWarning,
        stacklevel=2,
    )

    if issubclass(interfaces, IComponent):
        interfaces = [interfaces]
    else:
        # assert isinstance(interfaces, list)
        for i in interfaces:
            if not issubclass(i, IComponent):
                err_msg = "incorrect interfaces"
                raise TypeError(err_msg)

    def _wrapper(cls: type[_Imp]) -> type[_Imp]:
        class _Wrapper(cls, *interfaces):
            pass

        return _Wrapper

    return _wrapper


def import_string(dotted_path: str):
    """Dynamically import a class or attribute from a dotted module path.

    This function takes a dotted path string (e.g., "myapp.services.MyClass")
    and imports the module, then returns the specified attribute/class.

    This is useful for loading component implementations from configuration
    files where the class is specified as a string.

    Args:
        dotted_path: A dotted module path with the class/attribute name as
            the last component. Format: "module.path.ClassName"

    Returns:
        The imported class or attribute.

    Raises:
        ImportError: If the module path is invalid, the module cannot be
            imported, or the attribute does not exist in the module.

    Example:
        >>> CacheClass = import_string("fivcglue.implements.caches_mem.MemoryCacheImpl")
        >>> cache = CacheClass(_component_site=None)

        >>> # Invalid path
        >>> import_string("invalid")  # Raises ImportError
    """
    try:
        module_path, class_name = dotted_path.rsplit(".", 1)
    except ValueError as e:
        msg = f"{dotted_path} doesn't look like a module path"
        raise ImportError(msg) from e

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as e:
        msg = f'Module "{module_path}" does not define a "{class_name}" attribute/class'
        raise ImportError(msg) from e
