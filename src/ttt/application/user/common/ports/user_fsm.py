from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import overload


@dataclass(frozen=True)
class WaitingEmojiToBuyState: ...


@dataclass(frozen=True)
class WaitingEmojiToSelectState: ...


type UserFsmState = WaitingEmojiToBuyState | WaitingEmojiToSelectState


class InvalidUserFsmStateError(Exception): ...


class UserFsm(ABC):
    @abstractmethod
    @overload
    async def state[T: UserFsmState](
        self, type_: type[T],
    ) -> T: ...

    @abstractmethod
    @overload
    async def state[T: UserFsmState](
        self, type_: None,
    ) -> None: ...

    @abstractmethod
    async def state[T: UserFsmState](
        self, type_: type[T] | None,
    ) -> T | None:
        """
        :raises ttt.application.user.common.ports.InvalidUserFsmStateError:
        """

    @abstractmethod
    async def set(self, state: UserFsmState | None) -> None: ...
