from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from fivcglue import IComponent

if TYPE_CHECKING:
    from datetime import timedelta


class ICache(IComponent):
    """
    cache service
    """

    @abstractmethod
    def get_value(
        self,
        key_name: str,
    ) -> bytes | None:
        """
        get value by key name
        """

    @abstractmethod
    def set_value(
        self,
        key_name: str,
        value: bytes | None,
        expire: timedelta,  # always set expire time
    ) -> bool:
        """
        set value
        """
