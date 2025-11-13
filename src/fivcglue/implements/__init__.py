"""Default implementations of core component framework interfaces.

This module provides the standard implementations for:
- ComponentSite: In-memory component registry
- ComponentSiteBuilder: Configuration-based component loader

These implementations form the foundation of the FivcGlue dependency injection
framework, allowing components to be registered, retrieved, and configured from
external configuration files.
"""

from __future__ import annotations

from typing import TextIO

from fivcglue import (
    IComponent,
    IComponentSite,
    IComponentSiteBuilder,
)
from fivcglue import (
    utils as i_utils,
)


class ComponentSite(IComponentSite):
    """Default in-memory implementation of IComponentSite.

    ComponentSite maintains a registry of component instances organized by
    interface type and optional name. It provides methods to register, query,
    and retrieve components.

    The internal storage structure is:
    {interface_type: {name: component_instance}}

    This allows multiple implementations of the same interface to be registered
    with different names.

    Example:
        >>> site = ComponentSite()
        >>> cache = MemoryCacheImpl(_component_site=site)
        >>> site.register_component(ICache, cache, name="default")
        >>> retrieved = site.get_component(ICache, name="default")
    """

    def __init__(self):
        """Initialize an empty component registry."""
        self.service_mapping: dict[type, dict[str, IComponent]] = {}

    def get_component(
        self,
        interface: type,
        name: str = "",
    ) -> IComponent:
        """Get a component instance by interface type and name.

        Args:
            interface: The interface type to look up.
            name: Optional name to distinguish between multiple implementations.
                Defaults to empty string.

        Returns:
            The registered component instance.

        Raises:
            LookupError: If no component is found for the given interface and name.
        """
        component = self.query_component(interface, name=name)
        if not component:
            err_msg = "component not found"
            raise LookupError(err_msg)
        return component

    def query_component(
        self,
        interface: type,
        name: str = "",
    ) -> IComponent | None:
        """Query for a component instance by interface type and name.

        Args:
            interface: The interface type to look up.
            name: Optional name to distinguish between multiple implementations.
                Defaults to empty string.

        Returns:
            The registered component instance, or None if not found.
        """
        component = self.service_mapping.get(interface)
        return component and component.get(name)

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
            name: Optional name to distinguish between multiple implementations.
                Defaults to empty string.

        Returns:
            The registered component instance (same as implement parameter).

        Raises:
            TypeError: If the implement instance does not implement the interface.
        """
        if not issubclass(implement.__class__, interface):
            err_msg = "incorrect implementation for component interface"
            raise TypeError(err_msg)

        mapping = self.service_mapping.setdefault(interface, {})
        mapping.update({name: implement})
        return implement


class ComponentSiteBuilder(IComponentSiteBuilder):
    """Default implementation of IComponentSiteBuilder.

    ComponentSiteBuilder loads component configurations from JSON or YAML files
    and registers them with a component site. Configuration files specify:
    - Component class (dotted path)
    - Constructor parameters
    - Interface registrations with optional names

    Configuration format:
    [
        {
            "class": "module.path.ClassName",
            "param1": "value1",
            "entries": [
                {"interface": "module.IInterface", "name": "optional_name"}
            ]
        }
    ]

    Example:
        >>> builder = ComponentSiteBuilder()
        >>> site = ComponentSite()
        >>> with open("config.json") as f:
        ...     builder.loads(site, f, fmt="json")
    """

    @staticmethod
    def _loads(component_site: IComponentSite, configs: tuple | list):
        """Load component configurations from parsed data structure.

        Internal method that processes the parsed configuration data and
        registers components with the component site.

        Args:
            component_site: The component site to register components to.
            configs: Parsed configuration data as a list of component definitions.

        Raises:
            TypeError: If the configuration structure is invalid.
            LookupError: If a component class or interface cannot be found.
        """
        if not isinstance(configs, (tuple, list)):
            err_msg = "invalid component configuration file"
            raise TypeError(err_msg)

        for config_item in configs:
            service_class_name = config_item.pop("class", "")
            service_entries_name = config_item.pop("entries", [])
            if not isinstance(service_entries_name, (tuple, list)):
                err_msg = "invalid component entries in configuration file"
                raise TypeError(err_msg)
            try:
                service_class = i_utils.import_string(service_class_name)
            except ImportError as e:
                err_msg = f"invalid component class {service_class_name}"
                raise LookupError(err_msg) from e

            service_instance = service_class(component_site, **config_item)
            for e in service_entries_name:
                if not isinstance(e, dict):
                    err_msg = "invalid component entry in configuration file"
                    raise TypeError(err_msg)

                service_name = e.get("name", "")
                service_interface_name = e.get("interface", "")
                try:
                    service_interface = i_utils.import_string(service_interface_name)
                except ImportError as e:
                    err_msg = f"invalid component interface {service_interface_name}"
                    raise LookupError(err_msg) from e

                component_site.register_component(
                    service_interface, service_instance, name=service_name
                )

    def _parse(self, configs: TextIO, fmt: str = "json"):
        """Parse configuration file content into a data structure.

        Args:
            configs: Text stream containing the configuration data.
            fmt: Configuration format ("json", "yaml", or "yml").

        Returns:
            Parsed configuration data as a list or tuple.

        Raises:
            NotImplementedError: If the format is not supported.
        """
        if fmt == "json":
            import json

            return json.loads(configs.read())

        if fmt in ["yaml", "yml"]:
            import yaml

            return yaml.safe_load(configs.read())

        err_msg = f"Unknown file format {fmt}"
        raise NotImplementedError(err_msg)

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
        self._loads(component_site, self._parse(configs, fmt))

    def dumps(
        self,
        component_site: IComponentSite,
        configs: TextIO,
        fmt: str = "json",
    ):
        """Save component configurations from a component site to a file.

        This method is not currently implemented.

        Args:
            component_site: The component site to save components from.
            configs: Text stream to write the configuration data to.
            fmt: Configuration format. Supported values: "json", "yaml", "yml".
                Defaults to "json".

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError
