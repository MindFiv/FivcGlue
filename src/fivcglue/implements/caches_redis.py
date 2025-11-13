from __future__ import annotations

from typing import TYPE_CHECKING

from fivcglue import IComponentSite, utils
from fivcglue.interfaces import caches

if TYPE_CHECKING:
    from datetime import timedelta


@utils.implements(caches.ICache)
class CacheImpl:
    def __init__(
        self,
        _component_site: IComponentSite,
        **_kwargs,
    ):
        print("create cache of redis")  # noqa

    def get_value(
        self,
        key_name: str,
    ) -> bytes | None:
        pass

    def set_value(
        self,
        _key_name: str,
        _value: bytes | None,
        expire: timedelta,
    ) -> bool:
        return bool(expire.total_seconds())
