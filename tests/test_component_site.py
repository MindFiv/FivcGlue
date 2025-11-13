import unittest
from io import StringIO
from unittest.mock import patch

from fivcglue import IComponent
from fivcglue.implements import ComponentSite, ComponentSiteBuilder
from fivcglue.interfaces import configs


class MockComponent(IComponent):
    """Mock component for testing"""

    pass


class TestComponentSite(unittest.TestCase):
    def setUp(self):
        self.component_site = ComponentSite()

    def test_initialization(self):
        """Test ComponentSite initialization"""
        assert self.component_site.service_mapping == {}

    def test_register_component(self):
        """Test registering a component"""
        mock_component = MockComponent()

        result = self.component_site.register_component(IComponent, mock_component, name="test")

        assert result == mock_component
        assert IComponent in self.component_site.service_mapping
        assert self.component_site.service_mapping[IComponent]["test"] == mock_component

    def test_register_component_without_name(self):
        """Test registering a component without a name"""
        mock_component = MockComponent()

        result = self.component_site.register_component(IComponent, mock_component)

        assert result == mock_component
        assert self.component_site.service_mapping[IComponent][""] == mock_component

    def test_register_component_incorrect_type(self):
        """Test registering a component with incorrect type raises TypeError"""

        class NotAComponent:
            pass

        not_component = NotAComponent()

        with self.assertRaises(TypeError) as context:
            self.component_site.register_component(IComponent, not_component)

        assert "incorrect implementation for component interface" in str(context.exception)

    def test_query_component_found(self):
        """Test querying a registered component"""
        mock_component = MockComponent()
        self.component_site.register_component(IComponent, mock_component, name="test")

        result = self.component_site.query_component(IComponent, name="test")

        assert result == mock_component

    def test_query_component_not_found(self):
        """Test querying a non-existent component returns None"""
        result = self.component_site.query_component(IComponent, name="nonexistent")
        assert result is None

    def test_query_component_interface_not_registered(self):
        """Test querying an interface that was never registered"""
        result = self.component_site.query_component(configs.IConfig, name="test")
        assert result is None

    def test_get_component_found(self):
        """Test getting a registered component"""
        mock_component = MockComponent()
        self.component_site.register_component(IComponent, mock_component, name="test")

        result = self.component_site.get_component(IComponent, name="test")

        assert result == mock_component

    def test_get_component_not_found(self):
        """Test getting a non-existent component raises LookupError"""
        with self.assertRaises(LookupError) as context:
            self.component_site.get_component(IComponent, name="nonexistent")

        assert "component not found" in str(context.exception)


class TestComponentSiteBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = ComponentSiteBuilder()
        self.component_site = ComponentSite()

    def test_parse_json(self):
        """Test parsing JSON configuration"""
        json_config = '{"key": "value"}'
        config_io = StringIO(json_config)

        result = self.builder._parse(config_io, fmt="json")

        assert result == {"key": "value"}

    def test_parse_yaml(self):
        """Test parsing YAML configuration"""
        yaml_config = "key: value"
        config_io = StringIO(yaml_config)

        result = self.builder._parse(config_io, fmt="yaml")

        assert result == {"key": "value"}

    def test_parse_yml(self):
        """Test parsing YML configuration (alternative extension)"""
        yml_config = "key: value"
        config_io = StringIO(yml_config)

        result = self.builder._parse(config_io, fmt="yml")

        assert result == {"key": "value"}

    def test_parse_unknown_format(self):
        """Test parsing unknown format raises NotImplementedError"""
        config_io = StringIO("data")

        with self.assertRaises(NotImplementedError) as context:
            self.builder._parse(config_io, fmt="xml")

        assert "Unknown file format xml" in str(context.exception)

    def test_loads_invalid_config_type(self):
        """Test _loads with invalid config type raises TypeError"""
        with self.assertRaises(TypeError) as context:
            self.builder._loads(self.component_site, "not a list")

        assert "invalid component configuration file" in str(context.exception)

    def test_loads_invalid_entries_type(self):
        """Test _loads with invalid entries type raises TypeError"""
        configs = [{"class": "fivcglue.implements.ComponentSite", "entries": "not a list"}]

        with self.assertRaises(TypeError) as context:
            self.builder._loads(self.component_site, configs)

        assert "invalid component entries in configuration file" in str(context.exception)

    def test_loads_invalid_class_name(self):
        """Test _loads with invalid class name raises LookupError"""
        configs = [{"class": "nonexistent.module.Class", "entries": []}]

        with self.assertRaises(LookupError) as context:
            self.builder._loads(self.component_site, configs)

        assert "invalid component class" in str(context.exception)

    def test_loads_invalid_entry_type(self):
        """Test _loads with invalid entry type raises TypeError"""
        # Use a class that accepts component_site parameter
        configs = [
            {
                "class": "fivcglue.implements.loggers_builtin.LoggerSiteImpl",
                "entries": ["not a dict"],
            }
        ]

        with self.assertRaises(TypeError) as context:
            self.builder._loads(self.component_site, configs)

        assert "invalid component entry in configuration file" in str(context.exception)

    def test_loads_invalid_interface_name(self):
        """Test _loads with invalid interface name raises LookupError"""
        # Use a class that accepts component_site parameter
        configs = [
            {
                "class": "fivcglue.implements.loggers_builtin.LoggerSiteImpl",
                "entries": [{"name": "test", "interface": "nonexistent.module.Interface"}],
            }
        ]

        with self.assertRaises(LookupError) as context:
            self.builder._loads(self.component_site, configs)

        assert "invalid component interface" in str(context.exception)

    def test_dumps_not_implemented(self):
        """Test dumps raises NotImplementedError"""
        config_io = StringIO()

        with self.assertRaises(NotImplementedError):
            self.builder.dumps(self.component_site, config_io)

    def test_loads_integration(self):
        """Test loads method integration with JSON"""
        # Use a class that accepts component_site parameter
        json_config = """
        [
            {
                "class": "fivcglue.implements.loggers_builtin.LoggerSiteImpl",
                "entries": []
            }
        ]
        """
        config_io = StringIO(json_config)

        # Should not raise any exceptions (suppress print output)
        with patch("builtins.print"):
            self.builder.loads(self.component_site, config_io, fmt="json")
