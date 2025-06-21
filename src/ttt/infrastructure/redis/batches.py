from asyncio import sleep
from collections.abc import AsyncIterator
from dataclasses import dataclass
from secrets import randbelow
from typing import Literal, overload

from redis.asyncio import Redis

from ttt.entities.tools.assertion import assert_


@dataclass(frozen=True, unsafe_hash=False)
class InRedisFixedBatches:
    _redis: Redis
    _list_name: str
    _pulling_timeout_min_ms: int
    _pulling_timeout_salt_ms: int

    async def push(self, value: bytes, /) -> None:
        await self._redis.rpush(self._list_name, value)  # type: ignore[misc]

    @overload
    def with_len(
        self,
        batch_len: Literal[2],
    ) -> AsyncIterator[tuple[bytes, bytes]]: ...

    @overload
    def with_len(
        self,
        batch_len: Literal[3],
    ) -> AsyncIterator[tuple[bytes, bytes, bytes]]: ...

    @overload
    def with_len(
        self,
        batch_len: int,
    ) -> AsyncIterator[tuple[bytes, ...]]: ...

    async def with_len(
        self, batch_len: int,
    ) -> AsyncIterator[tuple[bytes, ...]]:
        assert_(batch_len >= 1)

        while True:
            await self._sleep()

            result = await self._redis.lmpop(  # type: ignore[misc]
                1,
                self._list_name,  # type: ignore[arg-type]
                direction="LEFT",
                count=batch_len,
            )
            if result is None:
                continue

            _, batch = result

            if len(batch) < batch_len:
                await self._redis.lpush(self._list_name, *batch)  # type: ignore[misc]

            yield tuple(batch)

    async def _sleep(self) -> None:
        sleep_ms = (
            self._pulling_timeout_min_ms
            + randbelow(self._pulling_timeout_salt_ms)
        )

        await sleep(sleep_ms / 1000)
