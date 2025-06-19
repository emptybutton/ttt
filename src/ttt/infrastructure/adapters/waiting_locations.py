from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import ClassVar, cast

from pydantic import TypeAdapter

from ttt.application.game.ports.waiting_locations import WaitingLocations
from ttt.entities.core.player.location import JustLocation
from ttt.infrastructure.redis.batches import InRedisFixedBatches


@dataclass(frozen=True, unsafe_hash=False)
class InRedisFixedBatchesWaitingLocations(WaitingLocations):
    _batches: InRedisFixedBatches

    _adapter: ClassVar = TypeAdapter(JustLocation)

    async def push(self, location: JustLocation, /) -> None:
        await self._batches.push(self._adapter.dump_json(location))

    async def __aiter__(
        self,
    ) -> AsyncIterator[tuple[JustLocation, JustLocation]]:
        async for location1_bytes, location2_bytes in self._batches.with_len(2):
            yield (
                self._entity(location1_bytes),
                self._entity(location2_bytes),
            )

    def _entity(self, bytes_: bytes) -> JustLocation:
        return cast(JustLocation, self._adapter.validate_json(bytes_))
