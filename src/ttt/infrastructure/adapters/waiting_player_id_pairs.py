from collections.abc import AsyncIterator
from dataclasses import dataclass

from ttt.application.game.ports.waiting_player_id_pairs import (
    WaitingPlayerIdPairs,
)
from ttt.infrastructure.redis.batches import InRedisBatches


@dataclass(frozen=True, unsafe_hash=False)
class InRedisWaitingPlayerIdPairs(WaitingPlayerIdPairs):
    _id_batches: InRedisBatches

    async def push(self, id_: int, /) -> None:
        await self._id_batches.push(str(id_).encode())

    async def __aiter__(self) -> AsyncIterator[tuple[int, int]]:
        async for id1, id2 in self._id_batches.with_len(2):
            yield (int(id1.decode()), int(id2.decode()))
