"""Core component interfaces for the FivcGlue dependency injection framework.

This module defines the fundamental interfaces for the component-based architecture:
- IComponent: Base interface for all components
- IComponentSite: Registry for managing component instances
- IComponentSiteBuilder: Builder for loading/saving component configurations

The component system follows a service locator pattern where components are registered
with a component site and can be retrieved by their interface type and optional name.
"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TextIO


class IComponent(metaclass=ABCMeta):  # noqa B024
    """Base interface for all components in the FivcGlue framework.

    This is the root interface that all component interfaces must inherit from.
    It serves as a marker interface to identify components within the system.
    Components are managed by IComponentSite and can be registered, queried,
    and retrieved through the component registry.

    Example:
        >>> class IMyService(IComponent):
        ...     @abstractmethod
        ...     def do_something(self) -> None:
        ...         pass
    """


class IComponentSite(metaclass=ABCMeta):
    """Component registry for managing and retrieving component instances.

    IComponentSite acts as a service locator that maintains a registry of component
    implementations. Components are registered with an interface type and optional name,
    and can be retrieved later using the same identifiers.

    The component site supports:
    - Registering components with interface types and optional names
    - Querying for components (returns None if not found)
    - Getting components (raises exception if not found)

    Example:
        >>> site = ComponentSite()
        >>> site.register_component(ICache, MemoryCacheImpl(), name="default")
        >>> cache = site.get_component(ICache, name="default")
    """

    @abstractmethod
    def get_component(
        self,
        interface: type,
        name: str = "",
    ) -> IComponent:
        """Get a component instance by interface type and name.

        Args:
            interface: The interface type to look up.
            name: Optional name to distinguish between multiple implementations
                of the same interface. Defaults to empty string.

        Returns:
            The registered component instance.

        Raises:
            LookupError: If no component is found for the given interface and name.
        """

    @abstractmethod
    def query_component(
        self,
        interface: type,
        name: str = "",
    ) -> IComponent | None:
        """Query for a component instance by interface type and name.

        Similar to get_component but returns None instead of raising an exception
        when the component is not found.

        Args:
            interface: The interface type to look up.
            name: Optional name to distinguish between multiple implementations
                of the same interface. Defaults to empty string.

        Returns:
            The registered component instance, or None if not found.
        """

    @abstractmethod
    def register_component(
        self,
        interface: type,
        implement: IComponent,
        name: str = "",
    ) -> IComponent:
        """Register a component implementation with the component site.

        Args:
            interface: The interface type that the component implements.
            implement: The component instance to register.
            name: Optional name to distinguish between multiple implementations
                of the same interface. Defaults to empty string.

        Returns:
            The registered component instance (same as implement parameter).

        Raises:
            TypeError: If the implement instance does not implement the interface.
        """


class IComponentSiteBuilder(metaclass=ABCMeta):
    """Builder interface for loading and saving component configurations.

    IComponentSiteBuilder provides methods to serialize and deserialize component
    configurations to/from various formats (JSON, YAML, etc.). This allows component
    sites to be configured from external configuration files.

    Example:
        >>> builder = ComponentSiteBuilder()
        >>> with open("config.json") as f:
        ...     builder.loads(component_site, f, fmt="json")
    """

    @abstractmethod
    def loads(
        self,
        component_site: IComponentSite,
        configs: TextIO,
        fmt: str = "json",
    ):
        """Load component configurations from a file and register them.

        Reads component configurations from the provided file stream, parses them
        according to the specified format, and registers the components with the
        component site.

        Args:
            component_site: The component site to register components to.
            configs: Text stream containing the configuration data.
            fmt: Configuration format. Supported values: "json", "yaml", "yml".
                Defaults to "json".

        Raises:
            TypeError: If the configuration format is invalid.
            LookupError: If a component class or interface cannot be found.
        """

    @abstractmethod
    def dumps(
        self,
        component_site: IComponentSite,
        configs: TextIO,
        fmt: str = "json",
    ):
        """Save component configurations from a component site to a file.

        Serializes the registered components from the component site and writes
        them to the provided file stream in the specified format.

        Args:
            component_site: The component site to save components from.
            configs: Text stream to write the configuration data to.
            fmt: Configuration format. Supported values: "json", "yaml", "yml".
                Defaults to "json".

        Raises:
            NotImplementedError: If this method is not implemented.
        """
