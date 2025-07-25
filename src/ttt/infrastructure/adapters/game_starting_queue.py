from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass
from typing import cast

from ttt.application.game.game.ports.game_starting_queue import (
    GameStartingQueue,
    GameStartingQueuePush,
)
from ttt.infrastructure.redis.batches import InRedisFixedBatches


@dataclass(frozen=True, unsafe_hash=False)
class InRedisFixedBatchesWaitingLocations(GameStartingQueue):
    _batches: InRedisFixedBatches

    async def push_many(self, user_ids: Sequence[int], /) -> None:
        if user_ids:
            await self._batches.add(map(self._bytes, user_ids))

    async def push(self, user_id: int, /) -> GameStartingQueuePush:
        push_code = await self._batches.add([self._bytes(user_id)])
        was_location_added_in_set = bool(push_code)

        return GameStartingQueuePush(
            was_location_dedublicated=not was_location_added_in_set,
        )

    async def __aiter__(
        self,
    ) -> AsyncIterator[tuple[int, int]]:
        async for user1_id_bytes, user2_id_bytes in self._batches.with_len(2):
            user1_id = self._user_id(user1_id_bytes)
            user2_id = self._user_id(user2_id_bytes)

            user_ids = (user1_id, user2_id)
            ok_user_ids = tuple(
                user_id for user_id in user_ids if user_id is not None
            )

            if len(user_ids) != len(ok_user_ids):
                await self._batches.add(map(self._bytes, ok_user_ids))
                continue

            yield cast(tuple[int, int], ok_user_ids)

    def _bytes(self, user_id: int) -> bytes:
        return str(user_id).encode()

    def _user_id(self, bytes_: bytes) -> int | None:
        try:
            return int(bytes_.decode())
        except ValueError:
            return None
