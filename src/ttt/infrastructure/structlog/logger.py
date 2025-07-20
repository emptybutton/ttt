from typing import cast

import structlog
from structlog.types import FilteringBoundLogger

from ttt.infrastructure.structlog.processors import AddRequestId


def logger() -> FilteringBoundLogger:
    return cast(FilteringBoundLogger, structlog.wrap_logger(
        structlog.PrintLogger(),
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.dict_tracebacks,
            AddRequestId(),
            structlog.dev.ConsoleRenderer(),
        ],
    ))
