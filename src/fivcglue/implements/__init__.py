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
    """
    default implementation of IComponentSite
    """

    def __init__(self):
        self.service_mapping: dict[type, dict[str, IComponent]] = {}

    def get_component(
        self,
        interface: type,
        name: str = "",
    ) -> IComponent:
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
        component = self.service_mapping.get(interface)
        return component and component.get(name)

    def register_component(
        self,
        interface: type,
        implement: IComponent,
        name: str = "",
    ) -> IComponent:
        if not issubclass(implement.__class__, interface):
            err_msg = "incorrect implementation for component interface"
            raise TypeError(err_msg)

        mapping = self.service_mapping.setdefault(interface, {})
        mapping.update({name: implement})
        return implement


class ComponentSiteBuilder(IComponentSiteBuilder):
    """
    default implementation of ServiceBuilder
    """

    @staticmethod
    def _loads(component_site: IComponentSite, configs: tuple | list):
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
        self._loads(component_site, self._parse(configs, fmt))

    def dumps(
        self,
        component_site: IComponentSite,
        configs: TextIO,
        fmt: str = "json",
    ):
        raise NotImplementedError
