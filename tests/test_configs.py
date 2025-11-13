import os
import unittest

from fivcglue.implements.utils import load_component_site
from fivcglue.interfaces import configs
from fivcglue.interfaces.utils import query_component


class TestConfigs(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ["CONFIG_JSON"] = "fixtures/test_env.json"
        os.environ["CONFIG_YAML"] = "fixtures/test_env.yml"

        cls.component_site = load_component_site(fmt="yaml")

    def test_config_json(self):
        config = query_component(self.component_site, configs.IConfig, "Json")
        assert config is not None
        config_sess = config.get_session("test")
        assert config_sess is not None
        config_val = config_sess.get_value("key1")
        assert config_val == "haha"

    def test_config_yaml(self):
        config = query_component(self.component_site, configs.IConfig, "Yaml")
        assert config is not None
        config_sess = config.get_session("test")
        assert config_sess is not None
        config_val = config_sess.get_value("key1")
        assert config_val == "haha"
