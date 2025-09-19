import logging
from typing import cast

import structlog
from structlog.types import FilteringBoundLogger
from structlog_sentry import SentryProcessor

from ttt.infrastructure.structlog.processors import AddRequestId


def dev_logger(*, with_request_id: bool) -> FilteringBoundLogger:
    renderer = structlog.dev.ConsoleRenderer(
        exception_formatter=(
            structlog.dev.RichTracebackFormatter(show_locals=False)
        ),
    )
    return cast(
        FilteringBoundLogger,
        structlog.wrap_logger(
            structlog.PrintLogger(),
            processors=[
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                *([AddRequestId()] if with_request_id else []),
                renderer,
            ],
        ),
    )


def prod_logger(*, with_request_id: bool) -> FilteringBoundLogger:
    return cast(
        FilteringBoundLogger,
        structlog.wrap_logger(
            structlog.PrintLogger(),
            processors=[
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso", utc=True),
                *([AddRequestId()] if with_request_id else []),
                SentryProcessor(event_level=logging.WARNING),
                structlog.processors.KeyValueRenderer(),
            ],
        ),
    )


async def unexpected_error_log(
    logger: FilteringBoundLogger,
    error: Exception,
) -> None:
    await logger.aexception("unexpected_error", exc_info=error)
