from asyncio import gather
from collections.abc import Sequence
from dataclasses import dataclass

from ttt.infrastructure.dishka.next_container import NextContainer
from ttt.infrastructure.processors.processor import Processor


@dataclass(frozen=True, unsafe_hash=False)
class Processors(Processor):
    _processors: Sequence[Processor]

    async def __call__(self, container: NextContainer) -> None:
        await gather(*(processor(container) for processor in self._processors))
