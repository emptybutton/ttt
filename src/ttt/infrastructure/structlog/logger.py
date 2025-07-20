import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import cast

import structlog
from structlog.types import FilteringBoundLogger
from structlog_sentry import SentryProcessor

from ttt.infrastructure.structlog.processors import AddRequestId


class LoggerFactory(ABC):
    @abstractmethod
    def __call__(self) -> FilteringBoundLogger: ...


@dataclass(frozen=True)
class DevLoggerFactory(LoggerFactory):
    def __call__(self) -> FilteringBoundLogger:
        return cast(FilteringBoundLogger, structlog.wrap_logger(
            structlog.PrintLogger(),
            processors=[
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                AddRequestId(),
                structlog.dev.ConsoleRenderer(),
            ],
        ))


@dataclass(frozen=True)
class ProdLoggerFactory(LoggerFactory):
    def __call__(self) -> FilteringBoundLogger:
        return cast(FilteringBoundLogger, structlog.wrap_logger(
            structlog.PrintLogger(),
            processors=[
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso", utc=True),
                AddRequestId(),
                SentryProcessor(event_level=logging.WARNING),
                structlog.processors.dict_tracebacks,
                structlog.processors.JSONRenderer(),
            ],
        ))
