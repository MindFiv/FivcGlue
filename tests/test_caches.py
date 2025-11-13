import unittest

from fivcglue import utils
from fivcglue.implements.utils import load_component_site
from fivcglue.interfaces import caches


class TestCaches(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.component_site = load_component_site(fmt="yaml")

    def test_cache_redis(self):
        cache = utils.query_component(self.component_site, caches.ICache, "Redis")
        assert cache is not None
        cache.get_value("test")
