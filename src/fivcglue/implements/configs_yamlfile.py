from __future__ import annotations

import os

from fivcglue import IComponentSite, utils
from fivcglue.interfaces import configs


@utils.implements(configs.IConfigSession)
class ConfigSessionImpl:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get_value(self, key_name: str) -> str | None:
        return self.kwargs.get(key_name)


@utils.implements(configs.IConfig)
class ConfigImpl:
    """
    implement config
    """

    def __init__(self, _component_site: IComponentSite, **_kwargs):
        print("create config component of yml file")  # noqa
        try:
            import yaml

            with open(os.environ.setdefault("CONFIG_YAML", ".env.yml")) as f:
                self.sessions = yaml.safe_load(f)
        except (FileNotFoundError, ValueError, TypeError):
            self.sessions = {}

    def get_session(self, name: str) -> ConfigSessionImpl:
        kwargs = self.sessions.get(name)
        kwargs = kwargs if isinstance(kwargs, dict) else {}
        return ConfigSessionImpl(**kwargs)
