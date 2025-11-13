from __future__ import annotations

from collections.abc import Callable
from importlib import import_module
from typing import (
    Any,
    TypeVar,
)

from . import IComponent, IComponentSite  # noqa

_Int = TypeVar("_Int")  # interface class
_Imp = TypeVar("_Imp")  # implement class


def cast_component(
    instance: Any,
    instance_type: type[_Int],
) -> _Int | None:
    return instance if isinstance(instance, instance_type) else None


def query_component(
    interface_site: IComponentSite,
    interface_type: type[_Int],
    name: str = "",
) -> _Int | None:
    i = interface_site.query_component(interface_type, name=name)
    return cast_component(i, interface_type) if i else None


def implements(interfaces: type[_Int] | list[type[_Int]]) -> Callable[[type[_Imp]], type[_Imp]]:
    if issubclass(interfaces, IComponent):
        interfaces = [interfaces]
    else:
        # assert isinstance(interfaces, list)
        for i in interfaces:
            if not issubclass(i, IComponent):
                err_msg = "incorrect interfaces"
                raise TypeError(err_msg)

    def _wrapper(cls: type[_Imp]) -> type[_Imp]:
        class _Wrapper(cls, *interfaces):
            def query_component(
                self,
                interface: type,
                name: str = "",  # noqa
            ) -> IComponent | None:
                if interface in interfaces:
                    return self
                return None

        return _Wrapper

    return _wrapper


def import_string(dotted_path: str):
    """
    Import a dotted module path and return the attribute/class
    designated by the last name in the path.
    Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit(".", 1)
    except ValueError as e:
        msg = f"{dotted_path} doesn't look like a module path"
        raise ImportError(msg) from e

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as e:
        msg = f'Module "{module_path}" does not define a "{class_name}" attribute/class'
        raise ImportError(msg) from e
