from collections.abc import Sequence
from dataclasses import dataclass
from functools import partial

from ttt.presentation.tasks.task import NextContainer, Task
from ttt.presentation.unkillable_task_group import UnkillableTaskGroup


@dataclass(frozen=True, unsafe_hash=False)
class UnkillableTasks(Task):
    _tasks: Sequence[Task]
    _group: UnkillableTaskGroup

    async def __call__(self, container: NextContainer) -> None:
        for task in self._tasks:
            self._group.add(partial(task, container))
