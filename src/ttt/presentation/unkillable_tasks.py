import asyncio
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from types import TracebackType
from typing import Any, Self


@dataclass(frozen=True, unsafe_hash=False)
class UnkillableTasks:
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

        await asyncio.gather(*self._tasks)

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
            except Exception as error:
                self._create_task(decorated_func())
                raise error from error

        return decorated_func

    def _create_task(self, coro: Coroutine[Any, Any, Any]) -> None:
        task = self._loop.create_task(coro)
        self._tasks.add(task)
