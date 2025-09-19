from asyncio import Semaphore, TaskGroup, sleep
from dataclasses import dataclass, field

from structlog.types import FilteringBoundLogger

from ttt.application.user.game.matchmake import Matchmake
from ttt.infrastructure.structlog.logger import unexpected_error_log
from ttt.presentation.tasks.task import NextContainer, Task


@dataclass
class MatchmakeTasks(Task):
    _max_workers: int
    _worker_creation_interval_seconds: float
    _logger: FilteringBoundLogger

    _semaphore: Semaphore = field(init=False)
    _task_group: TaskGroup = field(init=False, default_factory=TaskGroup)

    def __post_init__(self) -> None:
        self._semaphore = Semaphore(self._max_workers)

    async def __call__(self, container: NextContainer) -> None:
        async with self._task_group:
            while True:
                await sleep(self._worker_creation_interval_seconds)
                if not self._semaphore.locked():
                    self._task_group.create_task(self._matchmake(container))

    async def _matchmake(self, container: NextContainer) -> None:
        try:
            async with self._semaphore, container() as request:
                matchmake = await request.get(Matchmake)
                await matchmake()
        except Exception as error:  # noqa: BLE001
            await unexpected_error_log(self._logger, error)
