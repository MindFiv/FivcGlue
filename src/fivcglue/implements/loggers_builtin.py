from __future__ import annotations

from logging import Logger, getLogger
from traceback import format_exc

from fivcglue import IComponentSite, utils
from fivcglue.interfaces import loggers


@utils.implements(loggers.ILogger)
class LoggerImpl:
    """
    default logger
    """

    def __init__(self, logger: Logger):
        self.logger = logger

    def info(
        self,
        msg: str | None = None,
        attrs: dict | None = None,  # noqa
        error: Exception | None = None,
    ):
        err_msg = error and format_exc() or ""
        self.logger.info(msg or err_msg)

    def warning(
        self,
        msg: str | None = None,
        attrs: dict | None = None,  # noqa
        error: Exception | None = None,
    ):
        err_msg = error and format_exc() or ""
        self.logger.warning(msg or err_msg)

    def error(
        self,
        msg: str | None = None,
        attrs: dict | None = None,  # noqa
        error: Exception | None = None,
    ):
        err_msg = error and format_exc() or ""
        self.logger.error(msg or err_msg)


@utils.implements(loggers.ILoggerSite)
class LoggerSiteImpl:
    def __init__(self, _component_site: IComponentSite, **_kwargs):
        print("create logger site component of default")  # noqa

    def get_logger(self, topic: str):
        return LoggerImpl(getLogger(topic))
