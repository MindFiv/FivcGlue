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

    def test_config_json_list_keys(self):
        """Test list_keys method for JSON config implementation"""
        config = query_component(self.component_site, configs.IConfig, "Json")
        assert config is not None

        # Test session with multiple keys
        config_sess = config.get_session("test")
        assert config_sess is not None
        keys = config_sess.list_keys()
        assert isinstance(keys, list)
        assert len(keys) == 3
        assert "key1" in keys
        assert "key2" in keys
        assert "key3" in keys

        # Test empty session
        empty_sess = config.get_session("empty")
        assert empty_sess is not None
        empty_keys = empty_sess.list_keys()
        assert isinstance(empty_keys, list)
        assert len(empty_keys) == 0

    def test_config_yaml_list_keys(self):
        """Test list_keys method for YAML config implementation"""
        config = query_component(self.component_site, configs.IConfig, "Yaml")
        assert config is not None

        # Test session with multiple keys
        config_sess = config.get_session("test")
        assert config_sess is not None
        keys = config_sess.list_keys()
        assert isinstance(keys, list)
        assert len(keys) == 3
        assert "key1" in keys
        assert "key2" in keys
        assert "key3" in keys

        # Test empty session
        empty_sess = config.get_session("empty")
        assert empty_sess is not None
        empty_keys = empty_sess.list_keys()
        assert isinstance(empty_keys, list)
        assert len(empty_keys) == 0

    def test_config_list_keys_iteration(self):
        """Test iterating over keys returned by list_keys"""
        config = query_component(self.component_site, configs.IConfig, "Json")
        assert config is not None

        config_sess = config.get_session("test")
        assert config_sess is not None

        # Iterate over all keys and verify values can be retrieved
        keys = config_sess.list_keys()
        for key in keys:
            value = config_sess.get_value(key)
            assert value is not None
            assert isinstance(value, str)
