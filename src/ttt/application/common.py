from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from ttt.entities.core import Cell, Game, Player
from ttt.entities.math import Matrix, MatrixSize
from ttt.entities.tools import Tracking


type Transaction = AbstractAsyncContextManager[Any]


@dataclass(frozen=True)
class NoPlayerError(Exception):
    player_id: int


class Players(ABC):
    @abstractmethod
    async def assert_contains_player_with_id(self, id_: int, /) -> None:
        """
        :raises ttt.application.common.NoPlayerError:
        """

    @abstractmethod
    async def player_with_id(self, id_: int, /) -> Player:
        """
        :raises ttt.application.common.NoPlayerError:
        """

    @abstractmethod
    async def players_with_id(
        self, id1: int, id2: int, /,
    ) -> tuple[Player, Player]:
        """
        :raises ttt.application.common.NoPlayerError:
        """


class PlayerViews[PlayerWithIDViewT](ABC):
    @abstractmethod
    async def view_of_player_with_id(
        self, player_id: int, /,
    ) -> PlayerWithIDViewT: ...


class NotUniquePlayerIdError(Exception): ...


type MappableEntityLifeCycle = Tracking[Player | Game | Cell]


class Map(ABC):
    @abstractmethod
    async def __call__(
        self,
        effect: MappableEntityLifeCycle,
        /,
    ) -> None:
        """
        :raises ttt.application.common.NotUniquePlayerIdError:
        """


class WaitingPlayerIdPairs(ABC):
    @abstractmethod
    async def push(self, id_: int, /) -> None: ...

    @abstractmethod
    def __aiter__(self) -> AsyncIterator[tuple[int, int]]: ...


class NoGameError(Exception): ...


class Games(ABC):
    @abstractmethod
    async def game_with_id(self, id_: UUID | None, /) -> Game:
        """
        :raises ttt.application.common.NoGameError:
        """


class GameViews[GameViewT](ABC):
    @abstractmethod
    async def view_game_of_player_with_id(self, id_: int | None, /) -> GameViewT:
        ...


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


class UUIDs(ABC):
    @abstractmethod
    async def random_uuid(self) -> UUID: ...

    @abstractmethod
    async def random_uuid_matrix(self, size: MatrixSize) -> Matrix[UUID]: ...
