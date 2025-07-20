import structlog
from structlog.types import FilteringBoundLogger

from ttt.infrastructure.structlog.processors import AddRequestId


def logger() -> FilteringBoundLogger:
    return structlog.wrap_logger(  # type: ingore[no-any-return]
        structlog.PrintLogger(),
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.dict_tracebacks,
            AddRequestId(),
            structlog.dev.ConsoleRenderer(),
            # structlog.processors.JSONRenderer(),
        ],
    )
