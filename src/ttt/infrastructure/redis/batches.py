from asyncio import sleep
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Literal, overload

from redis.asyncio import Redis

from ttt.entities.tools.assertion import assert_


@dataclass(frozen=True, unsafe_hash=False)
class InRedisBatches:
    _redis: Redis
    _list_name: str
    _pulling_delay_seconds: int | float

    async def push(self, value: bytes, /) -> None:
        self._redis.rpush(self._list_name, value)

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

    async def with_len(
        self, batch_len: int,
    ) -> AsyncIterator[tuple[bytes, ...]]:
        assert_(batch_len > 1)

        while True:
            await sleep(self._pulling_delay_seconds)

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
