import asyncio
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from types import TracebackType
from typing import Any, Self

from structlog.types import FilteringBoundLogger

from ttt.infrastructure.structlog.logger import unexpected_error_log


@dataclass(frozen=True)
class ResultBuffer:
    _logger: FilteringBoundLogger
    _loop: asyncio.AbstractEventLoop = field(
        init=False,
        default_factory=asyncio.get_running_loop,
    )
    _tasks: set[asyncio.Task[Any]] = field(init=False, default_factory=set)