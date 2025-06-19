from dataclasses import dataclass

from aiogram.types.message import Message

from ttt.application.common.dto.player_message import (
    PlayerAlreadyRegisteredMessage,
    PlayerIsNotRegisteredMessage,
    PlayerMessage,
    PlayerRegisteredMessage,
)
from ttt.application.common.ports.player_message_sending import (
    PlayerMessageSending,
)
from ttt.presentation.aiogram.messages.command import (
    help_message,
    need_to_start_message,
)


@dataclass(frozen=True, unsafe_hash=True)
class AiogramPlayerMessageSending(PlayerMessageSending):
    _message: Message

    async def send_message(
        self, message: PlayerMessage, /,
    ) -> None:
        match message:
            case PlayerRegisteredMessage():
                await help_message(self._message)
            case PlayerIsNotRegisteredMessage():
                await need_to_start_message(self._message)
            case PlayerAlreadyRegisteredMessage():
                await help_message(self._message)
