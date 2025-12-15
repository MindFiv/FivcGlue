import unittest
from unittest.mock import MagicMock

import fakeredis

from fivcglue import IComponentSite
from fivcglue.implements.queues_redis import (
    QueueConsumerImpl,
    QueueProducerImpl,
    QueueSiteImpl,
)
from fivcglue.interfaces import configs, queues


class TestQueueProducerImpl(unittest.TestCase):
    """Test QueueProducerImpl functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.redis_client = fakeredis.FakeStrictRedis()
        self.queue_name = "test_queue"
        self.producer = QueueProducerImpl(self.redis_client, self.queue_name)

    def test_producer_is_component(self):
        """Test that QueueProducerImpl implements IQueueProducer"""
        assert isinstance(self.producer, queues.IQueueProducer)

    def test_produce_success(self):
        """Test successful message production"""
        message = b"test message"

        result = self.producer.produce(message)

        assert result is True

    def test_produce_no_subscribers(self):
        """Test produce returns True even with no subscribers"""
        message = b"test message"

        result = self.producer.produce(message)

        assert result is True

    def test_produce_multiple_messages(self):
        """Test producing multiple messages"""
        messages = [b"msg1", b"msg2", b"msg3"]

        for msg in messages:
            result = self.producer.produce(msg)
            assert result is True

    def test_produce_empty_message(self):
        """Test producing empty message"""
        message = b""

        result = self.producer.produce(message)

        assert result is True

    def test_produce_large_message(self):
        """Test producing large message"""
        message = b"x" * 1000000  # 1MB message

        result = self.producer.produce(message)

        assert result is True

    def test_produce_with_subscriber(self):
        """Test produce with actual subscriber"""
        # Create a consumer to subscribe
        consumer = QueueConsumerImpl(self.redis_client, self.queue_name)
        assert consumer
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(self.queue_name)

        # Produce a message
        message = b"test message"
        result = self.producer.produce(message)

        assert result is True

        # Verify message was published
        msg = pubsub.get_message(timeout=1)
        # First message is subscription confirmation
        assert msg["type"] == "subscribe"

        msg = pubsub.get_message(timeout=1)
        # Second message is the actual message
        assert msg["type"] == "message"
        assert msg["data"] == message

        pubsub.close()

    def test_produce_binary_data(self):
        """Test produce with various binary data"""
        binary_data = bytes(range(256))

        result = self.producer.produce(binary_data)

        assert result is True


class TestQueueConsumerImpl(unittest.TestCase):
    """Test QueueConsumerImpl functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.redis_client = fakeredis.FakeStrictRedis()
        self.queue_name = "test_queue"
        self.consumer = QueueConsumerImpl(self.redis_client, self.queue_name)

    def test_consumer_is_component(self):
        """Test that QueueConsumerImpl implements IQueueConsumer"""
        assert isinstance(self.consumer, queues.IQueueConsumer)

    def test_consume_single_message(self):
        """Test consuming a single message"""
        message_data = b"test message"

        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(self.queue_name)

        # Skip subscription confirmation
        msg = pubsub.get_message(timeout=1)
        assert msg["type"] == "subscribe"

        # Publish message after subscription
        self.redis_client.publish(self.queue_name, message_data)

        # Get the actual message
        msg = pubsub.get_message(timeout=1)
        assert msg["type"] == "message"
        assert msg["data"] == message_data

        pubsub.close()

    def test_consume_multiple_messages(self):
        """Test consuming multiple messages"""
        messages_data = [b"msg1", b"msg2", b"msg3"]

        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(self.queue_name)

        # Skip subscription confirmation
        msg = pubsub.get_message(timeout=1)
        assert msg["type"] == "subscribe"

        # Publish multiple messages
        for msg_data in messages_data:
            self.redis_client.publish(self.queue_name, msg_data)

        # Receive all messages
        received_messages = []
        for _ in range(len(messages_data)):
            msg = pubsub.get_message(timeout=1)
            assert msg["type"] == "message"
            received_messages.append(msg["data"])

        assert received_messages == messages_data
        pubsub.close()

    def test_consume_filters_subscription_messages(self):
        """Test that subscription messages are filtered out"""
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(self.queue_name)

        # Get subscription confirmation
        msg = pubsub.get_message(timeout=1)
        assert msg["type"] == "subscribe"

        # Publish messages
        self.redis_client.publish(self.queue_name, b"msg1")
        self.redis_client.publish(self.queue_name, b"msg2")

        # Receive messages (should only get message type, not subscribe)
        msg1 = pubsub.get_message(timeout=1)
        assert msg1["type"] == "message"
        assert msg1["data"] == b"msg1"

        msg2 = pubsub.get_message(timeout=1)
        assert msg2["type"] == "message"
        assert msg2["data"] == b"msg2"

        pubsub.close()

    def test_consume_empty_message(self):
        """Test consuming empty message"""
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(self.queue_name)

        # Skip subscription confirmation
        msg = pubsub.get_message(timeout=1)
        assert msg["type"] == "subscribe"

        # Publish empty message
        self.redis_client.publish(self.queue_name, b"")

        # Receive empty message
        msg = pubsub.get_message(timeout=1)
        assert msg["type"] == "message"
        assert msg["data"] == b""

        pubsub.close()

    def test_consume_binary_data(self):
        """Test consuming binary data"""
        binary_data = bytes(range(256))

        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(self.queue_name)

        # Skip subscription confirmation
        msg = pubsub.get_message(timeout=1)
        assert msg["type"] == "subscribe"

        # Publish binary data
        self.redis_client.publish(self.queue_name, binary_data)

        # Receive binary data
        msg = pubsub.get_message(timeout=1)
        assert msg["type"] == "message"
        assert msg["data"] == binary_data

        pubsub.close()


class TestQueueSiteImpl(unittest.TestCase):
    """Test QueueSiteImpl functionality"""

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

    def test_queue_site_initialization_success(self):
        """Test successful QueueSiteImpl initialization"""
        # Patch redis module to return fakeredis
        import sys

        original_redis = sys.modules.get("redis")

        try:
            # Create a mock redis module that returns fakeredis
            mock_redis_module = MagicMock()
            mock_redis_module.Redis = fakeredis.FakeStrictRedis
            sys.modules["redis"] = mock_redis_module

            queue_site = QueueSiteImpl(self.component_site)

            assert queue_site.connected is True
            assert queue_site.redis_client is not None
        finally:
            if original_redis is not None:
                sys.modules["redis"] = original_redis
            elif "redis" in sys.modules:
                del sys.modules["redis"]

    def test_get_producer_success(self):
        """Test getting a producer when connected"""
        import sys

        original_redis = sys.modules.get("redis")

        try:
            mock_redis_module = MagicMock()
            mock_redis_module.Redis = fakeredis.FakeStrictRedis
            sys.modules["redis"] = mock_redis_module

            queue_site = QueueSiteImpl(self.component_site)
            producer = queue_site.get_producer("test_queue")

            assert isinstance(producer, queues.IQueueProducer)
            assert isinstance(producer, QueueProducerImpl)
        finally:
            if original_redis is not None:
                sys.modules["redis"] = original_redis
            elif "redis" in sys.modules:
                del sys.modules["redis"]

    def test_get_consumer_success(self):
        """Test getting a consumer when connected"""
        import sys

        original_redis = sys.modules.get("redis")

        try:
            mock_redis_module = MagicMock()
            mock_redis_module.Redis = fakeredis.FakeStrictRedis
            sys.modules["redis"] = mock_redis_module

            queue_site = QueueSiteImpl(self.component_site)
            consumer = queue_site.get_consumer("test_queue")

            assert isinstance(consumer, queues.IQueueConsumer)
            assert isinstance(consumer, QueueConsumerImpl)
        finally:
            if original_redis is not None:
                sys.modules["redis"] = original_redis
            elif "redis" in sys.modules:
                del sys.modules["redis"]

    def test_multiple_producers_same_queue(self):
        """Test creating multiple producers for the same queue"""
        import sys

        original_redis = sys.modules.get("redis")

        try:
            mock_redis_module = MagicMock()
            mock_redis_module.Redis = fakeredis.FakeStrictRedis
            sys.modules["redis"] = mock_redis_module

            queue_site = QueueSiteImpl(self.component_site)
            producer1 = queue_site.get_producer("test_queue")
            producer2 = queue_site.get_producer("test_queue")

            # Should be different instances but same queue
            assert producer1 is not producer2
            assert producer1.queue_name == producer2.queue_name
        finally:
            if original_redis is not None:
                sys.modules["redis"] = original_redis
            elif "redis" in sys.modules:
                del sys.modules["redis"]

    def test_multiple_consumers_same_queue(self):
        """Test creating multiple consumers for the same queue"""
        import sys

        original_redis = sys.modules.get("redis")

        try:
            mock_redis_module = MagicMock()
            mock_redis_module.Redis = fakeredis.FakeStrictRedis
            sys.modules["redis"] = mock_redis_module

            queue_site = QueueSiteImpl(self.component_site)
            consumer1 = queue_site.get_consumer("test_queue")
            consumer2 = queue_site.get_consumer("test_queue")

            # Should be different instances but same queue
            assert consumer1 is not consumer2
            assert consumer1.queue_name == consumer2.queue_name
        finally:
            if original_redis is not None:
                sys.modules["redis"] = original_redis
            elif "redis" in sys.modules:
                del sys.modules["redis"]

    def test_producer_and_consumer_different_queues(self):
        """Test producer and consumer on different queues"""
        import sys

        original_redis = sys.modules.get("redis")

        try:
            mock_redis_module = MagicMock()
            mock_redis_module.Redis = fakeredis.FakeStrictRedis
            sys.modules["redis"] = mock_redis_module

            queue_site = QueueSiteImpl(self.component_site)
            producer = queue_site.get_producer("queue1")
            consumer = queue_site.get_consumer("queue2")

            assert producer.queue_name == "queue1"
            assert consumer.queue_name == "queue2"
        finally:
            if original_redis is not None:
                sys.modules["redis"] = original_redis
            elif "redis" in sys.modules:
                del sys.modules["redis"]


class TestQueueIntegration(unittest.TestCase):
    """Integration tests for queue producer and consumer"""

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

    def test_producer_consumer_workflow(self):
        """Test complete producer-consumer workflow"""
        import sys

        original_redis = sys.modules.get("redis")

        try:
            mock_redis_module = MagicMock()
            mock_redis_module.Redis = fakeredis.FakeStrictRedis
            sys.modules["redis"] = mock_redis_module

            queue_site = QueueSiteImpl(self.component_site)
            producer = queue_site.get_producer("test_queue")
            consumer = queue_site.get_consumer("test_queue")
            assert consumer

            # Create a pubsub subscription to receive messages
            pubsub = queue_site.redis_client.pubsub()
            pubsub.subscribe("test_queue")

            # Skip subscription confirmation
            msg = pubsub.get_message(timeout=1)
            assert msg["type"] == "subscribe"

            # Produce messages
            assert producer.produce(b"msg1") is True
            assert producer.produce(b"msg2") is True

            # Receive messages
            msg1 = pubsub.get_message(timeout=1)
            assert msg1["type"] == "message"
            assert msg1["data"] == b"msg1"

            msg2 = pubsub.get_message(timeout=1)
            assert msg2["type"] == "message"
            assert msg2["data"] == b"msg2"

            pubsub.close()
        finally:
            if original_redis is not None:
                sys.modules["redis"] = original_redis
            elif "redis" in sys.modules:
                del sys.modules["redis"]

    def test_queue_site_is_component(self):
        """Test that QueueSiteImpl is a component"""
        import sys

        original_redis = sys.modules.get("redis")

        try:
            mock_redis_module = MagicMock()
            mock_redis_module.Redis = fakeredis.FakeStrictRedis
            sys.modules["redis"] = mock_redis_module

            queue_site = QueueSiteImpl(self.component_site)

            assert isinstance(queue_site, queues.IQueueSite)
        finally:
            if original_redis is not None:
                sys.modules["redis"] = original_redis
            elif "redis" in sys.modules:
                del sys.modules["redis"]


if __name__ == "__main__":
    unittest.main()
