"""Configuration interfaces for managing application settings.

This module defines interfaces for hierarchical configuration management:
- IConfigSession: Represents a named group of configuration key-value pairs
- IConfig: Main configuration interface that provides access to config sessions

Configuration can be loaded from various sources (JSON files, YAML files, etc.)
and organized into named sessions for better organization.
"""

from __future__ import annotations

from abc import abstractmethod

from fivcglue import IComponent


class IConfigSession(IComponent):
    """Interface for a named configuration session containing key-value pairs.

    A configuration session represents a logical grouping of related configuration
    values. For example, you might have separate sessions for "database", "api",
    or "logging" configurations.

    All configuration values are returned as strings. Type conversion should be
    handled by the caller if needed.

    Example:
        >>> config = JSONConfigImpl(_component_site=None)
        >>> session = config.get_session("database")
        >>> host = session.get_value("host")  # Returns "localhost"
        >>> port = int(session.get_value("port"))  # Convert to int
    """

    @abstractmethod
    def get_value(
        self,
        key_name: str,
    ) -> str | None:
        """Retrieve a configuration value by key name.

        Args:
            key_name: The configuration key to look up.

        Returns:
            The configuration value as a string if found, None otherwise.
        """


class IConfig(IComponent):
    """Interface for configuration management with named sessions.

    IConfig provides access to configuration data organized into named sessions.
    Each session contains a set of key-value pairs. This allows for logical
    grouping of related configuration values.

    Implementations typically load configuration from external sources like
    JSON files, YAML files, environment variables, or remote configuration
    services.

    Example:
        >>> config = YAMLConfigImpl(_component_site=None)
        >>> db_session = config.get_session("database")
        >>> api_session = config.get_session("api")
    """

    @abstractmethod
    def get_session(
        self,
        session_name: str,
    ) -> IConfigSession | None:
        """Retrieve a configuration session by name.

        Args:
            session_name: The name of the configuration session to retrieve.

        Returns:
            The configuration session if found, None otherwise.
        """
