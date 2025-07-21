import asyncio
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from types import TracebackType
from typing import Any, Self

from structlog.types import FilteringBoundLogger

from ttt.infrastructure.structlog.logger import unexpected_error_log


@dataclass(frozen=True, unsafe_hash=False)
class UnkillableTasks:
    _logger: FilteringBoundLogger
    _loop: asyncio.AbstractEventLoop = field(
        init=False, default_factory=asyncio.get_running_loop,
    )
    _tasks: set[asyncio.Task[Any]] = field(init=False, default_factory=set)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        error_type: type[BaseException] | None,
        error: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        for task in self._tasks:
            task.cancel()

        errors = await asyncio.gather(*self._tasks, return_exceptions=True)
        errors.append(error)

        errors = [error for error in errors if isinstance(error, Exception)]

        if errors:
            raise ExceptionGroup("unhandled errors", errors)  # noqa: TRY003

    def add(
        self,
        func: Callable[[], Coroutine[Any, Any, Any]],
    ) -> None:
        decorated_func = self._decorator(func)
        self._create_task(decorated_func())

    def _decorator(
        self,
        func: Callable[[], Coroutine[Any, Any, Any]],
    ) -> Callable[[], Coroutine[Any, Any, Any]]:
        async def decorated_func() -> None:
            try:
                await func()
            except Exception as error:  # noqa: BLE001
                self._create_task(decorated_func())
                await unexpected_error_log(self._logger, error)

        return decorated_func

    def _create_task(self, coro: Coroutine[Any, Any, Any]) -> None:
        task = self._loop.create_task(coro)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
