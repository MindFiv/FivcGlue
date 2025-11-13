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
