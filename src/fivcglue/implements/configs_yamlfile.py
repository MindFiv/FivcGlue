"""YAML file-based configuration implementation.

This module provides configuration management using YAML files.
Configuration is loaded from a YAML file specified by the CONFIG_YAML
environment variable (defaults to ".env.yml").

The YAML file should have the following structure:
session_name:
  key1: value1
  key2: value2
"""

from __future__ import annotations

import os

from fivcglue import IComponentSite
from fivcglue.interfaces import configs


class ConfigSessionImpl(configs.IConfigSession):
    """YAML-based configuration session implementation.

    Represents a named group of configuration key-value pairs loaded
    from a YAML file. All values are stored and returned as strings.

    Args:
        **kwargs: Configuration key-value pairs for this session.

    Example:
        >>> session = ConfigSessionImpl(host="localhost", port="5432")
        >>> session.get_value("host")
        'localhost'
    """

    def __init__(self, **kwargs):
        """Initialize configuration session with key-value pairs.

        Args:
            **kwargs: Configuration key-value pairs.
        """
        self.kwargs = kwargs

    def list_keys(self) -> list[str]:
        """List all configuration keys available in this session.

        Returns all configuration key names present in the session, allowing
        you to discover what configuration values are available without
        needing to know the keys in advance.

        Returns:
            A list of all configuration key names in the session. Returns an
            empty list if the session contains no configuration keys.

        Example:
            >>> session = ConfigSessionImpl(host="localhost", port="5432")
            >>> keys = session.list_keys()
            >>> print(keys)
            ['host', 'port']
        """
        return list(self.kwargs.keys())

    def get_value(self, key_name: str) -> str | None:
        """Retrieve a configuration value by key name.

        Args:
            key_name: The configuration key to look up.

        Returns:
            The configuration value as a string if found, None otherwise.
        """
        return self.kwargs.get(key_name)

    def set_value(self, key_name: str, value: str) -> bool:
        """Set a configuration value by key name.

        Args:
            key_name: The configuration key to set.
            value: The value to set.

        Returns:
            True if the value was set successfully, False otherwise.

        Example:
            >>> session = ConfigSessionImpl(host="localhost")
            >>> session.set_value("port", "5432")
            True
            >>> session.get_value("port")
            '5432'
        """
        self.kwargs[key_name] = value
        return True

    def delete_value(self, key_name: str) -> bool:
        """Delete a configuration value by key name.

        Args:
            key_name: The configuration key to delete.

        Returns:
            True if the value was deleted successfully, False if the key
            does not exist.

        Example:
            >>> session = ConfigSessionImpl(host="localhost", port="5432")
            >>> session.delete_value("port")
            True
            >>> session.get_value("port")
            None
            >>> session.delete_value("nonexistent")
            False
        """
        if key_name in self.kwargs:
            del self.kwargs[key_name]
            return True
        return False


class ConfigImpl(configs.IConfig):
    """YAML file-based configuration implementation.

    Loads configuration from a YAML file and provides access to named
    configuration sessions. The YAML file path is determined by the
    CONFIG_YAML environment variable (defaults to ".env.yml").

    If the file is not found or contains invalid YAML, an empty
    configuration is used instead.

    Args:
        _component_site: Component site instance (required by component system).
        **_kwargs: Additional parameters (ignored).

    Example:
        >>> # With CONFIG_YAML=config.yml containing:
        >>> # database:
        >>> #   host: localhost
        >>> #   port: 5432
        >>> config = ConfigImpl(_component_site=site)
        >>> db_session = config.get_session("database")
        >>> db_session.get_value("host")
        'localhost'
    """

    def __init__(self, _component_site: IComponentSite, **_kwargs):
        """Initialize configuration from YAML file.

        Loads configuration from the file specified by CONFIG_YAML environment
        variable. If the file is not found or contains invalid YAML, initializes
        with an empty configuration.

        Args:
            _component_site: Component site instance (required by component system).
            **_kwargs: Additional parameters (ignored).
        """
        print("create config component of yml file")  # noqa
        try:
            import yaml

            with open(os.environ.setdefault("CONFIG_YAML", ".env.yml")) as f:
                self.sessions = yaml.safe_load(f)
        except (FileNotFoundError, ValueError, TypeError):
            self.sessions = {}

    def get_session(self, name: str) -> ConfigSessionImpl:
        """Retrieve a configuration session by name.

        Args:
            name: The name of the configuration session to retrieve.

        Returns:
            A configuration session containing the key-value pairs for the
            specified session name. Returns an empty session if the name
            is not found.
        """
        kwargs = self.sessions.get(name)
        kwargs = kwargs if isinstance(kwargs, dict) else {}
        return ConfigSessionImpl(**kwargs)
