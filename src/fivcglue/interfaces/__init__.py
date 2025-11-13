from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TextIO


class IComponent(metaclass=ABCMeta):
    """
    the root interface for component
    """

    @abstractmethod
    def query_component(
        self,
        interface: type,
        name: str = "",
    ) -> IComponent | None:
        """
        get another component by entry
        """


class IComponentSite(metaclass=ABCMeta):
    @abstractmethod
    def get_component(
        self,
        interface: type,
        name: str = "",
    ) -> IComponent:
        """
        get component instance by component entry
        raise exception if no component found
        """

    @abstractmethod
    def query_component(
        self,
        interface: type,
        name: str = "",
    ) -> IComponent | None:
        """
        query component instance by component entry
        """

    @abstractmethod
    def register_component(
        self,
        interface: type,
        implement: IComponent,
        name: str = "",
    ) -> IComponent:
        """
        register component with component entries
        """


class IComponentSiteBuilder(metaclass=ABCMeta):
    @abstractmethod
    def loads(
        self,
        component_site: IComponentSite,
        configs: TextIO,
        fmt: str = "json",
    ):
        """
        register component to component site by reading configuration file
        """

    @abstractmethod
    def dumps(
        self,
        component_site: IComponentSite,
        configs: TextIO,
        fmt: str = "json",
    ):
        """
        save component from component site to configuration file
        """
