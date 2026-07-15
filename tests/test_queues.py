import unittest
from datetime import timedelta
from unittest.mock import MagicMock, patch

import fakeredis.aioredis
import pytest

from fivcglue import IComponentSite
from fivcglue.implements.queues_redis import (
    QueueConsumerImpl,
    QueueProducerImpl,
    QueueSiteImpl,
)
from fivcglue.interfaces import configs, queues


def _make_async_redis():
    return fakeredis.aioredis.FakeRedis(decode_responses=False)


class TestQueueProducerImpl(unittest.TestCase):
    """Test QueueProducerImpl functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.redis_client = _make_async_redis()
        self.queue_name = "test_queue"
        self.producer = QueueProducerImpl(self.redis_client, self.queue_name)

    def test_producer_is_component(self):
        """Test that QueueProducerImpl implements IQueueProducer"""
        assert isinstance(self.producer, queues.IQueueProducer)

    def test_produce_success(self):
        """Test successful message production"""
        assert self.producer.produce(b"test message") is True

    def test_produce_no_subscribers(self):
        """Test produce returns True even with no subscribers"""
        assert self.producer.produce(b"test message") is True

    def test_produce_multiple_messages(self):
        """Test producing multiple messages"""
        for msg in [b"msg1", b"msg2", b"msg3"]:
            assert self.producer.produce(msg) is True

    def test_produce_empty_message(self):
        """Test producing empty message"""
        assert self.producer.produce(b"") is True

    def test_produce_large_message(self):
        """Test producing large message"""
        assert self.producer.produce(b"x" * 1000000) is True

    def test_produce_with_subscriber(self):
        """Test produce with actual consumer subscriber"""
        consumer = QueueConsumerImpl(self.redis_client, self.queue_name)
        assert consumer.consume() is None  # subscribe, no message yet

        message = b"test message"
        assert self.producer.produce(message) is True
        assert consumer.consume() == message

    def test_produce_binary_data(self):
        """Test produce with various binary data"""
        assert self.producer.produce(bytes(range(256))) is True


class TestQueueProducerAsync:
    @pytest.fixture
    def producer(self):
        return QueueProducerImpl(_make_async_redis(), "async_queue")

    @pytest.mark.asyncio
    async def test_produce_async(self, producer):
        assert await producer.produce_async(b"async message") is True


class TestQueueConsumerImpl(unittest.TestCase):
    """Test QueueConsumerImpl functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.redis_client = _make_async_redis()
        self.queue_name = "test_queue"
        self.consumer = QueueConsumerImpl(self.redis_client, self.queue_name)
        self.producer = QueueProducerImpl(self.redis_client, self.queue_name)

    def test_consumer_is_component(self):
        """Test that QueueConsumerImpl implements IQueueConsumer"""
        assert isinstance(self.consumer, queues.IQueueConsumer)

    def test_consume_none_when_empty(self):
        """timeout=None returns immediately with None when empty"""
        assert self.consumer.consume() is None

    def test_consume_single_message(self):
        """Test consuming a single message"""
        assert self.consumer.consume() is None  # subscribe
        assert self.producer.produce(b"test message") is True
        assert self.consumer.consume() == b"test message"

    def test_consume_multiple_messages(self):
        """Test consuming multiple messages"""
        assert self.consumer.consume() is None  # subscribe
        for msg in [b"msg1", b"msg2", b"msg3"]:
            assert self.producer.produce(msg) is True

        assert self.consumer.consume() == b"msg1"
        assert self.consumer.consume() == b"msg2"
        assert self.consumer.consume() == b"msg3"

    def test_consume_filters_subscription_messages(self):
        """Subscription confirmations are not returned as messages"""
        assert self.consumer.consume() is None
        assert self.producer.produce(b"msg1") is True
        assert self.consumer.consume() == b"msg1"

    def test_consume_empty_message(self):
        """Test consuming empty message"""
        assert self.consumer.consume() is None
        assert self.producer.produce(b"") is True
        assert self.consumer.consume() == b""

    def test_consume_binary_data(self):
        """Test consuming binary data"""
        binary_data = bytes(range(256))
        assert self.consumer.consume() is None
        assert self.producer.produce(binary_data) is True
        assert self.consumer.consume() == binary_data

    def test_consume_timeout_returns_none(self):
        """Finite timeout returns None when no message arrives"""
        assert self.consumer.consume() is None
        assert self.consumer.consume(timeout=timedelta(milliseconds=50)) is None


class TestQueueConsumerAsync:
    @pytest.fixture
    def clients(self):
        redis_client = _make_async_redis()
        producer = QueueProducerImpl(redis_client, "async_queue")
        consumer = QueueConsumerImpl(redis_client, "async_queue")
        return producer, consumer

    @pytest.mark.asyncio
    async def test_consume_async_empty(self, clients):
        _, consumer = clients
        assert await consumer.consume_async() is None

    @pytest.mark.asyncio
    async def test_consume_async_message(self, clients):
        producer, consumer = clients
        assert await consumer.consume_async() is None
        assert await producer.produce_async(b"hello") is True
        assert await consumer.consume_async() == b"hello"

    @pytest.mark.asyncio
    async def test_consume_async_timeout(self, clients):
        _, consumer = clients
        assert await consumer.consume_async() is None
        assert await consumer.consume_async(timeout=timedelta(milliseconds=50)) is None


class _QueueSiteTestBase(unittest.TestCase):
    """Shared setup for QueueSiteImpl tests"""

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

    def _patch_redis(self):
        return patch("redis.asyncio.Redis", fakeredis.aioredis.FakeRedis)


class TestQueueSiteImpl(_QueueSiteTestBase):
    """Test QueueSiteImpl functionality"""

    def test_queue_site_initialization_success(self):
        """Test successful QueueSiteImpl initialization"""
        with self._patch_redis():
            queue_site = QueueSiteImpl(self.component_site)

            assert queue_site.connected is True
            assert queue_site.redis_client is not None

    def test_get_producer_success(self):
        """Test getting a producer when connected"""
        with self._patch_redis():
            queue_site = QueueSiteImpl(self.component_site)
            producer = queue_site.get_producer("test_queue")

            assert isinstance(producer, queues.IQueueProducer)
            assert isinstance(producer, QueueProducerImpl)

    def test_get_consumer_success(self):
        """Test getting a consumer when connected"""
        with self._patch_redis():
            queue_site = QueueSiteImpl(self.component_site)
            consumer = queue_site.get_consumer("test_queue")

            assert isinstance(consumer, queues.IQueueConsumer)
            assert isinstance(consumer, QueueConsumerImpl)

    def test_multiple_producers_same_queue(self):
        """Test creating multiple producers for the same queue"""
        with self._patch_redis():
            queue_site = QueueSiteImpl(self.component_site)
            producer1 = queue_site.get_producer("test_queue")
            producer2 = queue_site.get_producer("test_queue")

            assert producer1 is not producer2
            assert producer1.queue_name == producer2.queue_name

    def test_multiple_consumers_same_queue(self):
        """Test creating multiple consumers for the same queue"""
        with self._patch_redis():
            queue_site = QueueSiteImpl(self.component_site)
            consumer1 = queue_site.get_consumer("test_queue")
            consumer2 = queue_site.get_consumer("test_queue")

            assert consumer1 is not consumer2
            assert consumer1.queue_name == consumer2.queue_name

    def test_producer_and_consumer_different_queues(self):
        """Test producer and consumer on different queues"""
        with self._patch_redis():
            queue_site = QueueSiteImpl(self.component_site)
            producer = queue_site.get_producer("queue1")
            consumer = queue_site.get_consumer("queue2")

            assert producer.queue_name == "queue1"
            assert consumer.queue_name == "queue2"


class TestQueueIntegration(_QueueSiteTestBase):
    """Integration tests for queue producer and consumer"""

    def test_producer_consumer_workflow(self):
        """Test complete producer-consumer workflow"""
        with self._patch_redis():
            queue_site = QueueSiteImpl(self.component_site)
            producer = queue_site.get_producer("test_queue")
            consumer = queue_site.get_consumer("test_queue")

            assert consumer.consume() is None
            assert producer.produce(b"msg1") is True
            assert producer.produce(b"msg2") is True
            assert consumer.consume() == b"msg1"
            assert consumer.consume() == b"msg2"

    def test_queue_site_is_component(self):
        """Test that QueueSiteImpl is a component"""
        with self._patch_redis():
            queue_site = QueueSiteImpl(self.component_site)

            assert isinstance(queue_site, queues.IQueueSite)


if __name__ == "__main__":
    unittest.main()
