import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
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
    adds_request_id: bool = field(kw_only=True)

    def __call__(self) -> FilteringBoundLogger:
        return cast(
            FilteringBoundLogger,
            structlog.wrap_logger(
                structlog.PrintLogger(),
                processors=[
                    structlog.processors.add_log_level,
                    structlog.processors.TimeStamper(fmt="iso"),
                    *([AddRequestId()] if self.adds_request_id else []),
                    structlog.dev.ConsoleRenderer(),
                ],
            ),
        )


@dataclass(frozen=True)
class ProdLoggerFactory(LoggerFactory):
    adds_request_id: bool = field(kw_only=True)

    def __call__(self) -> FilteringBoundLogger:
        return cast(
            FilteringBoundLogger,
            structlog.wrap_logger(
                structlog.PrintLogger(),
                processors=[
                    structlog.processors.add_log_level,
                    structlog.processors.TimeStamper(fmt="iso", utc=True),
                    *([AddRequestId()] if self.adds_request_id else []),
                    SentryProcessor(event_level=logging.WARNING),
                    structlog.processors.dict_tracebacks,
                    structlog.processors.JSONRenderer(),
                ],
            ),
        )


async def unexpected_error_log(
    logger: FilteringBoundLogger,
    error: Exception,
) -> None:
    await logger.aexception("unexpected_error", exc_info=error)
