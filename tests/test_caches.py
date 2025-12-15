import os
import unittest
from datetime import timedelta
from unittest.mock import MagicMock, patch

from fivcglue import IComponentSite, utils
from fivcglue.implements.caches_redis import CacheImpl as RedisCacheImpl
from fivcglue.implements.utils import load_component_site
from fivcglue.interfaces import caches, configs


class TestCaches(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ["CONFIG_JSON"] = "fixtures/test_env.json"
        os.environ["CONFIG_YAML"] = "fixtures/test_env.yml"
        cls.component_site = load_component_site(fmt="yaml")

    def test_cache_redis(self):
        cache = utils.query_component(self.component_site, caches.ICache, "Redis")
        assert cache is not None
        cache.get_value("test")


class TestRedisCacheErrorHandling(unittest.TestCase):
    """Test error handling and edge cases for Redis cache implementation"""

    def setUp(self):
        """Set up test fixtures"""
        self.component_site = MagicMock(spec=IComponentSite)
        self._setup_config_mock()

    def _setup_config_mock(self):
        """Helper to set up config mock for Redis configuration"""
        mock_config_session = MagicMock(spec=configs.IConfigSession)
        mock_config_session.get_value.side_effect = lambda key: {
            "host": "localhost",
            "port": "6379",
            "db": "0",
            "password": "",
        }.get(key)

        mock_config = MagicMock(spec=configs.IConfig)
        mock_config.get_session.return_value = mock_config_session

        self.component_site.query_component.return_value = mock_config

    def test_set_value_with_zero_expiration(self):
        """Test set_value with zero or negative expiration time"""
        # Create a mock Redis module and client
        mock_redis_module = MagicMock()
        mock_redis_client = MagicMock()
        mock_redis_module.Redis.return_value = mock_redis_client
        mock_redis_client.ping.return_value = True

        with patch.dict("sys.modules", {"redis": mock_redis_module}):
            cache = RedisCacheImpl(self.component_site)

            # Test with zero expiration
            result = cache.set_value("test_key", b"test_value", timedelta(seconds=0))
            assert result is False

            # Test with negative expiration
            result = cache.set_value("test_key", b"test_value", timedelta(seconds=-5))
            assert result is False

    def test_set_value_with_none_value(self):
        """Test set_value with None as the value"""
        mock_redis_module = MagicMock()
        mock_redis_client = MagicMock()
        mock_redis_module.Redis.return_value = mock_redis_client
        mock_redis_client.ping.return_value = True
        mock_redis_client.setex.return_value = True

        with patch.dict("sys.modules", {"redis": mock_redis_module}):
            cache = RedisCacheImpl(self.component_site)

            # set_value with None should store empty bytes
            result = cache.set_value("test_key", None, timedelta(seconds=10))
            assert result is True

            # Verify setex was called with empty bytes
            mock_redis_client.setex.assert_called_once_with("test_key", 10, b"")

    def test_get_value_exception_handling(self):
        """Test get_value handles exceptions gracefully"""
        mock_redis_module = MagicMock()
        mock_redis_client = MagicMock()
        mock_redis_module.Redis.return_value = mock_redis_client
        mock_redis_client.ping.return_value = True
        mock_redis_client.get.side_effect = Exception("Redis error")

        with patch.dict("sys.modules", {"redis": mock_redis_module}):
            cache = RedisCacheImpl(self.component_site)

            # Should return None instead of raising
            value = cache.get_value("test_key")
            assert value is None

    def test_set_value_exception_handling(self):
        """Test set_value handles exceptions gracefully"""
        mock_redis_module = MagicMock()
        mock_redis_client = MagicMock()
        mock_redis_module.Redis.return_value = mock_redis_client
        mock_redis_client.ping.return_value = True
        mock_redis_client.setex.side_effect = Exception("Redis error")

        with patch.dict("sys.modules", {"redis": mock_redis_module}):
            cache = RedisCacheImpl(self.component_site)

            # Should return False instead of raising
            result = cache.set_value("test_key", b"value", timedelta(seconds=10))
            assert result is False

    def test_redis_connection_failure(self):
        """Test handling when Redis connection fails"""
        mock_redis_module = MagicMock()
        mock_redis_client = MagicMock()
        mock_redis_module.Redis.return_value = mock_redis_client
        mock_redis_client.ping.side_effect = Exception("Connection refused")

        with patch.dict("sys.modules", {"redis": mock_redis_module}):
            cache = RedisCacheImpl(self.component_site)

            # Should not be connected
            assert cache.connected is False
            assert cache.redis_client is None
