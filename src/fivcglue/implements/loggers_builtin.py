"""Built-in Python logging implementation.

This module provides logging functionality using Python's built-in logging module.
It wraps the standard library's Logger class to implement the ILogger interface
and provides a factory for creating topic-specific loggers.
"""

from __future__ import annotations

from logging import Logger, getLogger
from traceback import format_exc

from fivcglue import IComponentSite
from fivcglue.interfaces import loggers


class LoggerImpl(loggers.ILogger):
    """Built-in Python logger implementation.

    Wraps Python's standard logging.Logger to implement the ILogger interface.
    Supports logging messages, exceptions with tracebacks, and structured
    attributes (though attributes are currently ignored).

    Args:
        logger: The underlying Python Logger instance to wrap.

    Example:
        >>> import logging
        >>> logging.basicConfig(level=logging.INFO)
        >>> logger = LoggerImpl(getLogger("myapp"))
        >>> logger.info(msg="Application started")
        >>> try:
        ...     risky_operation()
        ... except Exception as e:
        ...     logger.error(msg="Operation failed", error=e)
    """

    def __init__(self, logger: Logger):
        """Initialize logger wrapper.

        Args:
            logger: The Python Logger instance to wrap.
        """
        self.logger = logger

    def info(
        self,
        msg: str | None = None,
        attrs: dict | None = None,  # noqa
        error: Exception | None = None,
    ):
        """Log an informational message.

        Args:
            msg: The log message. If not provided and error is given,
                the error traceback will be logged.
            attrs: Additional structured attributes (currently ignored).
            error: An exception to log. If provided, the full traceback
                will be included.
        """
        err_msg = error and format_exc() or ""
        self.logger.info(msg or err_msg)

    def warning(
        self,
        msg: str | None = None,
        attrs: dict | None = None,  # noqa
        error: Exception | None = None,
    ):
        """Log a warning message.

        Args:
            msg: The log message. If not provided and error is given,
                the error traceback will be logged.
            attrs: Additional structured attributes (currently ignored).
            error: An exception to log. If provided, the full traceback
                will be included.
        """
        err_msg = error and format_exc() or ""
        self.logger.warning(msg or err_msg)

    def error(
        self,
        msg: str | None = None,
        attrs: dict | None = None,  # noqa
        error: Exception | None = None,
    ):
        """Log an error message.

        Args:
            msg: The log message. If not provided and error is given,
                the error traceback will be logged.
            attrs: Additional structured attributes (currently ignored).
            error: An exception to log. If provided, the full traceback
                will be included.
        """
        err_msg = error and format_exc() or ""
        self.logger.error(msg or err_msg)


class LoggerSiteImpl(loggers.ILoggerSite):
    """Built-in Python logger factory implementation.

    Creates LoggerImpl instances using Python's built-in logging module.
    Each topic gets its own logger instance from logging.getLogger().

    Args:
        _component_site: Component site instance (required by component system).
        **_kwargs: Additional parameters (ignored).

    Example:
        >>> site = ComponentSite()
        >>> logger_site = LoggerSiteImpl(_component_site=site)
        >>> api_logger = logger_site.get_logger("api")
        >>> db_logger = logger_site.get_logger("database")
    """

    def __init__(self, _component_site: IComponentSite, **_kwargs):
        """Initialize logger site.

        Args:
            _component_site: Component site instance (required by component system).
            **_kwargs: Additional parameters (ignored).
        """
        print("create logger site component of default")  # noqa

    def get_logger(self, topic: str):
        """Create or retrieve a logger for the specified topic.

        Uses Python's logging.getLogger() to create or retrieve a logger
        with the given topic name.

        Args:
            topic: The topic/name for the logger.

        Returns:
            A LoggerImpl instance for the specified topic.
        """
        return LoggerImpl(getLogger(topic))
