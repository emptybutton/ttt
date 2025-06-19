from abc import ABC, abstractmethod

from ttt.application.common.dto.player_message import PlayerMessage


class PlayerMessageSending(ABC):
    @abstractmethod
    async def send_message(self, message: PlayerMessage, /) -> None: ...
