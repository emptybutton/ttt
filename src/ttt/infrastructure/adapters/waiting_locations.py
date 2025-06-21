from asyncio import gather
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass
from typing import ClassVar, cast

from pydantic import TypeAdapter

from ttt.application.game.ports.waiting_locations import WaitingLocations
from ttt.entities.core.player.location import PlayerLocation
from ttt.infrastructure.redis.batches import InRedisFixedBatches


@dataclass(frozen=True, unsafe_hash=False)
class InRedisFixedBatchesWaitingLocations(WaitingLocations):
    _batches: InRedisFixedBatches

    _adapter: ClassVar = TypeAdapter(PlayerLocation)

    async def push_many(self, locations: Sequence[PlayerLocation], /) -> None:
        await gather(*(self.push(location) for location in locations))

    async def push(self, location: PlayerLocation, /) -> None:
        await self._batches.push(self._adapter.dump_json(location))

    async def __aiter__(
        self,
    ) -> AsyncIterator[tuple[PlayerLocation, PlayerLocation]]:
        async for location1_bytes, location2_bytes in self._batches.with_len(2):
            yield (
                self._entity(location1_bytes),
                self._entity(location2_bytes),
            )

    def _entity(self, bytes_: bytes) -> PlayerLocation:
        return cast(PlayerLocation, self._adapter.validate_json(bytes_))
