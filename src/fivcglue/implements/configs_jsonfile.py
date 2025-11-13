from __future__ import annotations

import json
import os

from fivcglue import IComponentSite, utils
from fivcglue.interfaces import configs


@utils.implements(configs.IConfigSession)
class ConfigSessionImp:
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
        print("create config component of json file")  # noqa
        try:
            filename = os.environ.setdefault("CONFIG_JSON", ".env.json")
            with open(filename) as file:
                self.sessions = json.loads(file.read())
        except (FileNotFoundError, ValueError, TypeError):
            self.sessions = {}

    def get_session(self, name: str) -> ConfigSessionImp:
        kwargs = self.sessions.get(name)
        kwargs = kwargs if isinstance(kwargs, dict) else {}
        return ConfigSessionImp(**kwargs)
