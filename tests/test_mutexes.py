import unittest
from datetime import timedelta

from fivcglue import IComponent
from fivcglue.interfaces.mutexes import IMutex, IMutexSite


class MockMutex(IMutex):
    """Mock implementation of IMutex for testing"""

    def __init__(self):
        self.acquired = False
        self.released = False

    def acquire(self, expire: timedelta, method: str = "blocking") -> bool:
        """Mock acquire implementation"""
        self.acquired = True
        return True

    def release(self) -> bool:
        """Mock release implementation"""
        self.released = True
        return True


class MockMutexSite(IMutexSite):
    """Mock implementation of IMutexSite for testing"""

    def __init__(self):
        self.mutexes = {}

    def get_mutex(self, mtx_name: str) -> IMutex | None:
        """Mock get_mutex implementation"""
        if mtx_name not in self.mutexes:
            self.mutexes[mtx_name] = MockMutex()
        return self.mutexes[mtx_name]


class TestIMutex(unittest.TestCase):
    def setUp(self):
        self.mutex = MockMutex()

    def test_mutex_is_component(self):
        """Test that IMutex is a subclass of IComponent"""
        assert isinstance(self.mutex, IComponent)

    def test_acquire_blocking(self):
        """Test acquiring mutex with blocking method"""
        expire = timedelta(seconds=30)
        result = self.mutex.acquire(expire, method="blocking")

        assert result is True
        assert self.mutex.acquired is True

    def test_acquire_non_blocking(self):
        """Test acquiring mutex with non-blocking method"""
        expire = timedelta(seconds=30)
        result = self.mutex.acquire(expire, method="non-blocking")

        assert result is True
        assert self.mutex.acquired is True

    def test_acquire_default_method(self):
        """Test acquiring mutex with default method"""
        expire = timedelta(seconds=30)
        result = self.mutex.acquire(expire)

        assert result is True
        assert self.mutex.acquired is True

    def test_release(self):
        """Test releasing mutex"""
        result = self.mutex.release()

        assert result is True
        assert self.mutex.released is True

    def test_acquire_and_release(self):
        """Test full acquire and release cycle"""
        expire = timedelta(seconds=30)

        # Acquire
        acquire_result = self.mutex.acquire(expire)
        assert acquire_result is True
        assert self.mutex.acquired is True

        # Release
        release_result = self.mutex.release()
        assert release_result is True
        assert self.mutex.released is True


class TestIMutexSite(unittest.TestCase):
    def setUp(self):
        self.mutex_site = MockMutexSite()

    def test_mutex_site_is_component(self):
        """Test that IMutexSite is a subclass of IComponent"""
        assert isinstance(self.mutex_site, IComponent)

    def test_get_mutex(self):
        """Test getting a mutex by name"""
        mutex = self.mutex_site.get_mutex("test_mutex")

        assert mutex is not None
        assert isinstance(mutex, IMutex)

    def test_get_mutex_same_name_returns_same_instance(self):
        """Test getting mutex with same name returns same instance"""
        mutex1 = self.mutex_site.get_mutex("test_mutex")
        mutex2 = self.mutex_site.get_mutex("test_mutex")

        assert mutex1 == mutex2

    def test_get_mutex_different_names(self):
        """Test getting mutexes with different names"""
        mutex1 = self.mutex_site.get_mutex("mutex1")
        mutex2 = self.mutex_site.get_mutex("mutex2")

        assert mutex1 is not None
        assert mutex2 is not None
        assert mutex1 != mutex2

    def test_get_mutex_empty_name(self):
        """Test getting mutex with empty name"""
        mutex = self.mutex_site.get_mutex("")

        assert mutex is not None
        assert isinstance(mutex, IMutex)


class TestMutexIntegration(unittest.TestCase):
    def test_mutex_lifecycle(self):
        """Test complete mutex lifecycle through mutex site"""
        mutex_site = MockMutexSite()

        # Get mutex
        mutex = mutex_site.get_mutex("integration_test")
        assert mutex is not None

        # Acquire mutex
        expire = timedelta(seconds=60)
        acquired = mutex.acquire(expire, method="blocking")
        assert acquired is True

        # Release mutex
        released = mutex.release()
        assert released is True

    def test_multiple_mutexes_independent(self):
        """Test that multiple mutexes are independent"""
        mutex_site = MockMutexSite()

        mutex1 = mutex_site.get_mutex("mutex1")
        mutex2 = mutex_site.get_mutex("mutex2")

        # Acquire mutex1
        expire = timedelta(seconds=30)
        mutex1.acquire(expire)

        # mutex2 should not be affected
        assert mutex1.acquired is True
        assert mutex2.acquired is False

        # Release mutex1
        mutex1.release()

        # mutex2 should still not be affected
        assert mutex1.released is True
        assert mutex2.released is False
