from __future__ import annotations

from abc import abstractmethod

from fivcglue import IComponent


class ILogger(IComponent):
    """
    logger
    """

    @abstractmethod
    def info(
        self,
        msg: str | None = None,
        attrs: dict | None = None,
        error: Exception | None = None,
    ) -> None:
        """
        log info
        """

    @abstractmethod
    def warning(
        self,
        msg: str | None = None,
        attrs: dict | None = None,
        error: Exception | None = None,
    ) -> None:
        """
        log warning
        """

    @abstractmethod
    def error(
        self,
        msg: str | None = None,
        attrs: dict | None = None,
        error: Exception | None = None,
    ) -> None:
        """
        log error
        """


class ILoggerSite(IComponent):
    """
    logger site
    """

    @abstractmethod
    def get_logger(self, topic: str) -> ILogger:
        """
        get logger by topic
        """
