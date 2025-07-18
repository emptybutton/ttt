from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass
from typing import ClassVar, cast

from pydantic import TypeAdapter

from ttt.application.game.common.ports.waiting_locations import (
    WaitingLocations,
    WaitingLocationsPush,
)
from ttt.entities.core.user.location import UserLocation
from ttt.infrastructure.redis.batches import InRedisFixedBatches


@dataclass(frozen=True, unsafe_hash=False)
class InRedisFixedBatchesWaitingLocations(WaitingLocations):
    _batches: InRedisFixedBatches

    _adapter: ClassVar = TypeAdapter(UserLocation)

    async def push_many(self, locations: Sequence[UserLocation], /) -> None:
        if locations:
            await self._batches.add(map(self._bytes, locations))

    async def push(self, location: UserLocation, /) -> WaitingLocationsPush:
        push_code = await self._batches.add([self._bytes(location)])
        was_location_added_in_set = bool(push_code)

        return WaitingLocationsPush(
            was_location_dedublicated=not was_location_added_in_set,
        )

    async def __aiter__(
        self,
    ) -> AsyncIterator[tuple[UserLocation, UserLocation]]:
        async for location1_bytes, location2_bytes in self._batches.with_len(2):
            yield (
                self._entity(location1_bytes),
                self._entity(location2_bytes),
            )

    def _entity(self, bytes_: bytes) -> UserLocation:
        return cast(UserLocation, self._adapter.validate_json(bytes_))

    def _bytes(self, entity: UserLocation) -> bytes:
        return cast(bytes, self._adapter.dump_json(entity))
