from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import overload

from ttt.application.game.dto.game_message import GameMessage
from ttt.entities.telegram.message import MessageGlobalID


class GameMessageSending(ABC):
    @abstractmethod
    @overload
    async def send_messages(
        self, messages: tuple[GameMessage, GameMessage], /,
    ) -> tuple[MessageGlobalID, MessageGlobalID]: ...

    @abstractmethod
    @overload
    async def send_messages(
        self, messages: Sequence[GameMessage], /,
    ) -> tuple[MessageGlobalID, ...]: ...

    @abstractmethod
    async def send_messages(
        self, messages: Sequence[GameMessage], /,
    ) -> tuple[MessageGlobalID, ...]: ...

    @abstractmethod
    async def send_message(
        self, message: GameMessage, /,
    ) -> None: ...
