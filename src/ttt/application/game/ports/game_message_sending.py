from abc import ABC, abstractmethod
from collections.abc import Sequence

from ttt.application.game.dto.game_message import GameMessage


class GameMessageSending(ABC):
    @abstractmethod
    async def send_messages(
        self, messages: Sequence[GameMessage], /,
    ) -> None: ...

    @abstractmethod
    async def send_message(
        self, message: GameMessage, /,
    ) -> None: ...
