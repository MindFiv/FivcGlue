import unittest
from logging import getLogger
from unittest.mock import patch

from fivcglue.implements import ComponentSite
from fivcglue.implements.loggers_builtin import LoggerImpl, LoggerSiteImpl


class TestLoggerImpl(unittest.TestCase):
    def setUp(self):
        self.logger = getLogger("test_logger")
        self.logger_impl = LoggerImpl(self.logger)

    def test_info_with_message(self):
        """Test info logging with a message"""
        with patch.object(self.logger, "info") as mock_info:
            self.logger_impl.info(msg="Test info message")
            mock_info.assert_called_once_with("Test info message")

    def test_info_with_error(self):
        """Test info logging with an error"""
        with patch.object(self.logger, "info") as mock_info:
            try:
                raise ValueError("Test error")
            except ValueError as e:
                self.logger_impl.info(error=e)
                # Should log the traceback
                mock_info.assert_called_once()
                call_args = mock_info.call_args[0][0]
                assert "ValueError" in call_args
                assert "Test error" in call_args

    def test_info_with_attrs(self):
        """Test info logging with attributes (attrs are ignored but shouldn't cause errors)"""
        with patch.object(self.logger, "info") as mock_info:
            self.logger_impl.info(msg="Test message", attrs={"key": "value"})
            mock_info.assert_called_once_with("Test message")

    def test_warning_with_message(self):
        """Test warning logging with a message"""
        with patch.object(self.logger, "warning") as mock_warning:
            self.logger_impl.warning(msg="Test warning message")
            mock_warning.assert_called_once_with("Test warning message")

    def test_warning_with_error(self):
        """Test warning logging with an error"""
        with patch.object(self.logger, "warning") as mock_warning:
            try:
                raise RuntimeError("Test warning error")
            except RuntimeError as e:
                self.logger_impl.warning(error=e)
                # Should log the traceback
                mock_warning.assert_called_once()
                call_args = mock_warning.call_args[0][0]
                assert "RuntimeError" in call_args
                assert "Test warning error" in call_args

    def test_error_with_message(self):
        """Test error logging with a message"""
        with patch.object(self.logger, "error") as mock_error:
            self.logger_impl.error(msg="Test error message")
            mock_error.assert_called_once_with("Test error message")

    def test_error_with_error(self):
        """Test error logging with an error"""
        with patch.object(self.logger, "error") as mock_error:
            try:
                raise Exception("Test exception")
            except Exception as e:
                self.logger_impl.error(error=e)
                # Should log the traceback
                mock_error.assert_called_once()
                call_args = mock_error.call_args[0][0]
                assert "Exception" in call_args
                assert "Test exception" in call_args


class TestLoggerSiteImpl(unittest.TestCase):
    def test_logger_site_creation(self):
        """Test LoggerSiteImpl creation"""
        component_site = ComponentSite()

        # Capture print output
        with patch("builtins.print") as mock_print:
            logger_site = LoggerSiteImpl(component_site)
            mock_print.assert_called_once_with("create logger site component of default")
            assert logger_site is not None

    def test_get_logger(self):
        """Test getting a logger from LoggerSiteImpl"""
        component_site = ComponentSite()

        with patch("builtins.print"):
            logger_site = LoggerSiteImpl(component_site)
            logger = logger_site.get_logger("test_topic")

            assert logger is not None
            assert isinstance(logger, LoggerImpl)
            assert logger.logger.name == "test_topic"

    def test_get_logger_different_topics(self):
        """Test getting loggers for different topics"""
        component_site = ComponentSite()

        with patch("builtins.print"):
            logger_site = LoggerSiteImpl(component_site)
            logger1 = logger_site.get_logger("topic1")
            logger2 = logger_site.get_logger("topic2")

            assert logger1.logger.name == "topic1"
            assert logger2.logger.name == "topic2"
            assert logger1.logger != logger2.logger
