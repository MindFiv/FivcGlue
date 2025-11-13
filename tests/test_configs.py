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

    def test_config_json_set_value(self):
        """Test set_value method for JSON config implementation"""
        config = query_component(self.component_site, configs.IConfig, "Json")
        assert config is not None

        config_sess = config.get_session("test")
        assert config_sess is not None

        # Set a new value
        result = config_sess.set_value("new_key", "new_value")
        assert result is True

        # Verify the value was set
        value = config_sess.get_value("new_key")
        assert value == "new_value"

        # Verify new key appears in list_keys
        keys = config_sess.list_keys()
        assert "new_key" in keys

        # Update existing value
        result = config_sess.set_value("key1", "updated_value")
        assert result is True
        value = config_sess.get_value("key1")
        assert value == "updated_value"

    def test_config_yaml_set_value(self):
        """Test set_value method for YAML config implementation"""
        config = query_component(self.component_site, configs.IConfig, "Yaml")
        assert config is not None

        config_sess = config.get_session("test")
        assert config_sess is not None

        # Set a new value
        result = config_sess.set_value("new_key", "new_value")
        assert result is True

        # Verify the value was set
        value = config_sess.get_value("new_key")
        assert value == "new_value"

        # Verify new key appears in list_keys
        keys = config_sess.list_keys()
        assert "new_key" in keys

        # Update existing value
        result = config_sess.set_value("key1", "updated_value")
        assert result is True
        value = config_sess.get_value("key1")
        assert value == "updated_value"

    def test_config_json_delete_value(self):
        """Test delete_value method for JSON config implementation"""
        config = query_component(self.component_site, configs.IConfig, "Json")
        assert config is not None

        config_sess = config.get_session("test")
        assert config_sess is not None

        # Verify key exists before deletion
        value = config_sess.get_value("key2")
        assert value == "value2"
        assert "key2" in config_sess.list_keys()

        # Delete existing key
        result = config_sess.delete_value("key2")
        assert result is True

        # Verify key was deleted
        value = config_sess.get_value("key2")
        assert value is None
        assert "key2" not in config_sess.list_keys()

        # Try to delete non-existent key
        result = config_sess.delete_value("non_existent_key")
        assert result is False

        # Try to delete already deleted key
        result = config_sess.delete_value("key2")
        assert result is False

    def test_config_yaml_delete_value(self):
        """Test delete_value method for YAML config implementation"""
        config = query_component(self.component_site, configs.IConfig, "Yaml")
        assert config is not None

        config_sess = config.get_session("test")
        assert config_sess is not None

        # Verify key exists before deletion
        value = config_sess.get_value("key3")
        assert value == "value3"
        assert "key3" in config_sess.list_keys()

        # Delete existing key
        result = config_sess.delete_value("key3")
        assert result is True

        # Verify key was deleted
        value = config_sess.get_value("key3")
        assert value is None
        assert "key3" not in config_sess.list_keys()

        # Try to delete non-existent key
        result = config_sess.delete_value("non_existent_key")
        assert result is False

        # Try to delete already deleted key
        result = config_sess.delete_value("key3")
        assert result is False

    def test_config_set_and_delete_workflow(self):
        """Test complete workflow of set, get, and delete operations"""
        config = query_component(self.component_site, configs.IConfig, "Json")
        assert config is not None

        config_sess = config.get_session("test")
        assert config_sess is not None

        # Set multiple new values
        config_sess.set_value("temp1", "temporary_value_1")
        config_sess.set_value("temp2", "temporary_value_2")
        config_sess.set_value("temp3", "temporary_value_3")

        # Verify all were set
        assert config_sess.get_value("temp1") == "temporary_value_1"
        assert config_sess.get_value("temp2") == "temporary_value_2"
        assert config_sess.get_value("temp3") == "temporary_value_3"

        # Verify they appear in list_keys
        keys = config_sess.list_keys()
        assert "temp1" in keys
        assert "temp2" in keys
        assert "temp3" in keys

        # Delete one
        config_sess.delete_value("temp2")
        assert config_sess.get_value("temp2") is None
        assert "temp2" not in config_sess.list_keys()

        # Others should still exist
        assert config_sess.get_value("temp1") == "temporary_value_1"
        assert config_sess.get_value("temp3") == "temporary_value_3"

    def test_config_empty_session_operations(self):
        """Test operations on empty session"""
        config = query_component(self.component_site, configs.IConfig, "Json")
        assert config is not None

        empty_sess = config.get_session("empty")
        assert empty_sess is not None

        # Empty session should have no keys
        assert len(empty_sess.list_keys()) == 0

        # Getting non-existent key should return None
        assert empty_sess.get_value("any_key") is None

        # Deleting non-existent key should return False
        assert empty_sess.delete_value("any_key") is False

        # Set a value in empty session
        result = empty_sess.set_value("first_key", "first_value")
        assert result is True
        assert empty_sess.get_value("first_key") == "first_value"
        assert len(empty_sess.list_keys()) == 1

    def test_config_overwrite_value_multiple_times(self):
        """Test overwriting the same key multiple times"""
        config = query_component(self.component_site, configs.IConfig, "Yaml")
        assert config is not None

        config_sess = config.get_session("test")
        assert config_sess is not None

        # Set initial value
        config_sess.set_value("multi_update", "value1")
        assert config_sess.get_value("multi_update") == "value1"

        # Update multiple times
        for i in range(2, 10):
            config_sess.set_value("multi_update", f"value{i}")
            assert config_sess.get_value("multi_update") == f"value{i}"

        # Key should still appear only once in list_keys
        keys = config_sess.list_keys()
        count = sum(1 for k in keys if k == "multi_update")
        assert count == 1
