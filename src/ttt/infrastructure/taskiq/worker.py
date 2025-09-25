from asyncio import Event, TaskGroup, gather
from dataclasses import dataclass, field
from types import TracebackType
from typing import Self

from taskiq.receiver import Receiver


@dataclass
class TaskiqBgWorker:
    _receivers: tuple[Receiver, ...]

    _task_group: TaskGroup = field(init=False, default_factory=TaskGroup)
    _is_finished: Event = field(init=False, default_factory=Event)

    async def __aenter__(self) -> Self:
        await self._task_group.__aenter__()
        return self

    async def __call__(self) -> None:
        await gather(*(
            receiver.broker.startup()
            for receiver in self._receivers
        ))

        for receiver in self._receivers:
            self._task_group.create_task(receiver.listen(self._is_finished))

    async def __aexit__(
        self,
        error_type: type[BaseException] | None,
        error: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._is_finished.set()
        await self._task_group.__aexit__(error_type, error, traceback)
