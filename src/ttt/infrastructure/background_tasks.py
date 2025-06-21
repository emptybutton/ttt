import asyncio
from collections.abc import Coroutine
from dataclasses import dataclass, field
from types import TracebackType
from typing import Any, Self


@dataclass(frozen=True, unsafe_hash=False)
class BackgroundTasks:
    _loop: asyncio.AbstractEventLoop = field(
        default_factory=asyncio.get_running_loop,
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
        errors = [error for error in errors if isinstance(error, Exception)]

        if errors:
            raise ExceptionGroup("unhandled errors", errors)  # noqa: TRY003

    def create_task[T](self, coro: Coroutine[Any, Any, T]) -> asyncio.Task[T]:
        task = self._loop.create_task(coro)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

        return task
