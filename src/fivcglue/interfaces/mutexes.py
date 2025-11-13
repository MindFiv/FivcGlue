from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from fivcglue import IComponent

if TYPE_CHECKING:
    from datetime import timedelta


class IMutex(IComponent):
    """
    mutex session
    """

    @abstractmethod
    def acquire(
        self,
        expire: timedelta,
        method: str = "blocking",
    ) -> bool:
        """
        acquire mutex
        """

    @abstractmethod
    def release(self) -> bool:
        """
        release mutex
        """


class IMutexSite(IComponent):
    """
    mutex site
    """

    @abstractmethod
    def get_mutex(self, mtx_name: str) -> IMutex | None:
        """
        get mutex by name
        """
