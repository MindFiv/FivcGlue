"""Logging interfaces for structured application logging.

This module defines interfaces for logging functionality:
- ILogger: Interface for logging messages at different severity levels
- ILoggerSite: Factory interface for creating topic-specific loggers

Loggers support structured logging with messages, attributes, and exception tracking.
"""

from __future__ import annotations

from abc import abstractmethod

from fivcglue import IComponent


class ILogger(IComponent):
    """Interface for logging messages at different severity levels.

    ILogger provides methods for logging at three severity levels: info, warning,
    and error. Each method supports:
    - Plain text messages
    - Structured attributes (dict)
    - Exception/error objects with automatic traceback formatting

    Implementations may output to console, files, remote logging services, etc.

    Example:
        >>> logger = logger_site.get_logger("myapp.service")
        >>> logger.info(msg="User logged in", attrs={"user_id": "123"})
        >>> try:
        ...     risky_operation()
        ... except Exception as e:
        ...     logger.error(msg="Operation failed", error=e)
    """

    @abstractmethod
    def info(
        self,
        msg: str | None = None,
        attrs: dict | None = None,
        error: Exception | None = None,
    ) -> None:
        """Log an informational message.

        Args:
            msg: The log message. Optional if error is provided.
            attrs: Additional structured attributes to include in the log.
                May be ignored by some implementations.
            error: An exception to log. If provided, the traceback will be
                included in the log output.
        """

    @abstractmethod
    def warning(
        self,
        msg: str | None = None,
        attrs: dict | None = None,
        error: Exception | None = None,
    ) -> None:
        """Log a warning message.

        Args:
            msg: The log message. Optional if error is provided.
            attrs: Additional structured attributes to include in the log.
                May be ignored by some implementations.
            error: An exception to log. If provided, the traceback will be
                included in the log output.
        """

    @abstractmethod
    def error(
        self,
        msg: str | None = None,
        attrs: dict | None = None,
        error: Exception | None = None,
    ) -> None:
        """Log an error message.

        Args:
            msg: The log message. Optional if error is provided.
            attrs: Additional structured attributes to include in the log.
                May be ignored by some implementations.
            error: An exception to log. If provided, the traceback will be
                included in the log output.
        """


class ILoggerSite(IComponent):
    """Factory interface for creating topic-specific loggers.

    ILoggerSite provides a centralized way to create and manage loggers
    organized by topic. Topics typically represent different parts of the
    application (e.g., "api", "database", "auth").

    Example:
        >>> logger_site = LoggerSiteImpl(_component_site=None)
        >>> api_logger = logger_site.get_logger("api")
        >>> db_logger = logger_site.get_logger("database")
    """

    @abstractmethod
    def get_logger(self, topic: str) -> ILogger:
        """Create or retrieve a logger for the specified topic.

        Args:
            topic: The topic/name for the logger. This typically represents
                a module, component, or functional area of the application.

        Returns:
            A logger instance configured for the specified topic.
        """
