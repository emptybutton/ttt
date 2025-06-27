from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import overload


@dataclass(frozen=True)
class WaitingEmojiToBuyState: ...


@dataclass(frozen=True)
class WaitingEmojiToSelectState: ...


type PlayerFsmState = WaitingEmojiToBuyState | WaitingEmojiToSelectState


class InvalidPlayerFsmStateError(Exception): ...


class PlayerFsm(ABC):
    @abstractmethod
    @overload
    async def state[T: PlayerFsmState](
        self, type_: type[T],
    ) -> T: ...

    @abstractmethod
    @overload
    async def state[T: PlayerFsmState](
        self, type_: None,
    ) -> None: ...

    @abstractmethod
    async def state[T: PlayerFsmState](
        self, type_: type[T] | None,
    ) -> T | None:
        """
        :raises ttt.application.player.ports.InvalidPlayerFsmStateError:
        """

    @abstractmethod
    async def set(self, state: PlayerFsmState | None) -> None: ...
