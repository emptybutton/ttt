from asyncio import sleep
from collections.abc import AsyncIterator, Awaitable, Iterable
from dataclasses import dataclass
from secrets import randbelow
from typing import Literal, cast, overload

from redis.asyncio import Redis

from ttt.entities.tools.assertion import assert_


@dataclass(frozen=True, unsafe_hash=False)
class InRedisFixedBatches:
    _redis: Redis
    _sorted_set_name: str
    _pulling_timeout_min_ms: int
    _pulling_timeout_salt_ms: int

    async def add(self, batch: Iterable[bytes], /) -> Literal[0, 1]:
        seconds, _ = await cast(Awaitable[tuple[int, int]], self._redis.time())
        mapping = dict.fromkeys(batch, seconds)
        return cast(
            Literal[0, 1],
            await self._redis.zadd(self._sorted_set_name, mapping),
        )

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

            result = await self._redis.zmpop(  # type: ignore[misc]
                1,
                [self._sorted_set_name],
                min=True,
                count=batch_len,
            )
            if result is None:
                continue

            result = cast(tuple[bytes, list[tuple[bytes, bytes]]], result)
            _, values_with_score = result
            batch = tuple(
                value_and_score[0] for value_and_score in values_with_score
            )

            if len(batch) == batch_len:
                yield tuple(batch)
            else:
                await self.add(batch)

    async def _sleep(self) -> None:
        sleep_ms = (
            self._pulling_timeout_min_ms
            + randbelow(self._pulling_timeout_salt_ms)
        )

        await sleep(sleep_ms / 1000)
