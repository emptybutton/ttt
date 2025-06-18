from asyncio import sleep
from collections.abc import Awaitable
from dataclasses import dataclass
from typing import ClassVar, cast

from pydantic import TypeAdapter
from redis.asyncio import Redis

from ttt.application.game.ports.game_waiting_channel import (
    GameWaitingChannelMessage,
    GameWaitingChannelTimeoutError,
)
from ttt.entities.tools.assertion import assert_
from ttt.infrastructure.pydantic.game_waiting_channel_message import (
    EncodableGameWaitingChannelMessage,
    encodable_game_waiting_channel_message,
)


@dataclass(frozen=True, unsafe_hash=False)
class InRedisGameWaitingChannel:
    _redis: Redis
    _hash_name: str
    _message_ttl_ms: int
    _number_retries_to_wait: int
    _waiting_delay_seconds: float

    _adapter: ClassVar = TypeAdapter(
        EncodableGameWaitingChannelMessage,
    )

    def __post_init__(self) -> None:
        assert_(self._number_retries_to_wait >= 1)
        assert_(self._waiting_delay_seconds > 0)

    async def publish_many(
        self, messages: tuple[GameWaitingChannelMessage, ...],
    ) -> None:
        mapping = {
            str(message.player_id): self._message_json(message)
            for message in messages
        }
        await cast(Awaitable[int], self._redis.hsetex(
            self._hash_name, mapping=mapping, px=self._message_ttl_ms,
        ))

    async def wait(self, player_id: int) -> (
        GameWaitingChannelMessage | GameWaitingChannelTimeoutError
    ):
        for _ in range(self._number_retries_to_wait):
            await sleep(self._waiting_delay_seconds)

            message_json, *_ = await cast(Awaitable[list[bytes | None]],
                self._redis.hgetdel(self._hash_name, str(player_id)),
            )
            if message_json is None:
                continue

            encodable_message = self._adapter.validate_json(message_json)
            encodable_message = cast(
                EncodableGameWaitingChannelMessage, encodable_message,
            )
            return encodable_message.entity()

        return GameWaitingChannelTimeoutError()

    def _message_json(self, message: GameWaitingChannelMessage) -> str:
        return encodable_game_waiting_channel_message(message).model_dump_json()
