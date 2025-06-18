from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GameWaitingChannelOkMessage:
    player_id: int
    game_id: UUID


@dataclass(frozen=True)
class GameWaitingChannelPlayerInGameMessage(Exception):  # noqa: N818
    player_id: int


@dataclass(frozen=True)
class GameWaitingChannelNoGameMessage(Exception):  # noqa: N818
    player_id: int


type GameWaitingChannelMessage = (
    GameWaitingChannelOkMessage
    | GameWaitingChannelPlayerInGameMessage
    | GameWaitingChannelNoGameMessage
)


class GameWaitingChannelTimeoutError(Exception): ...


class GameWaitingChannel(ABC):
    @abstractmethod
    async def publish_many(
        self, messages: tuple[GameWaitingChannelMessage, ...],
    ) -> None: ...

    @abstractmethod
    async def wait(self, player_id: int) -> (
        GameWaitingChannelMessage | GameWaitingChannelTimeoutError
    ):
        ...
