"""Utility functions for component site management.

This module provides convenience functions for loading and configuring
component sites from configuration files.
"""

from __future__ import annotations

from os import path
from typing import TYPE_CHECKING

from fivcglue.implements import (
    ComponentSite,
    ComponentSiteBuilder,
)

if TYPE_CHECKING:
    from fivcglue import IComponentSite


def load_component_site(
    filename: str = "",
    fmt: str = "json",
    site: IComponentSite | None = None,
) -> IComponentSite:
    """Load a component site from a configuration file.

    Convenience function that creates a component site and loads component
    configurations from a file. If no filename is provided, loads the default
    basic configuration from the fixtures directory.

    Args:
        filename: Path to the configuration file. If empty, loads the default
            configuration from fixtures/configs_basics.yml.
        fmt: Configuration file format ("json", "yaml", or "yml").
            Defaults to "json", but is overridden to "yml" when using the
            default fixture file.
        site: Existing component site to load into. If None, creates a new
            ComponentSite instance.

    Returns:
        The component site with loaded components.

    Raises:
        FileNotFoundError: If the specified configuration file does not exist.
        TypeError: If the configuration file format is invalid.
        LookupError: If a component class or interface cannot be found.

    Example:
        >>> # Load from custom config file
        >>> site = load_component_site("myconfig.json", fmt="json")
        >>> cache = site.get_component(ICache)

        >>> # Load default configuration
        >>> site = load_component_site()

        >>> # Load into existing site
        >>> site = ComponentSite()
        >>> load_component_site("additional.yml", fmt="yml", site=site)
    """
    site = site or ComponentSite()
    site_builder = ComponentSiteBuilder()

    if not filename:
        fmt = "yml"
        filename = path.join(
            path.dirname(path.dirname(path.realpath(__file__))), "fixtures", "configs_basics.yml"
        )

    with open(filename) as f:
        site_builder.loads(site, f, fmt=fmt)
    return site
