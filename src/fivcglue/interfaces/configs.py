from __future__ import annotations

from abc import abstractmethod

from fivcglue import IComponent


class IConfigSession(IComponent):
    """
    config session
    """

    @abstractmethod
    def get_value(
        self,
        key_name: str,
    ) -> str | None:
        """
        get value by key
        """


class IConfig(IComponent):
    """
    config
    """

    @abstractmethod
    def get_session(
        self,
        session_name: str,
    ) -> IConfigSession | None:
        """
        get config session by name
        """
