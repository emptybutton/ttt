from asyncio import gather
from collections.abc import Sequence
from dataclasses import dataclass

from aiogram import Bot

from ttt.application.game.dto.game_message import (
    DoubleWaitingForGameMessage,
    GameMessage,
    PlayerAlreadyInGameMessage,
    WaitingForGameMessage,
)
from ttt.application.game.ports.game_message_sending import GameMessageSending
from ttt.entities.core.player.location import PlayerLocation
from ttt.infrastructure.background_tasks import BackgroundTasks
from ttt.presentation.aiogram.game.messages import (
    double_waiting_for_game_message,
    player_already_in_game_message,
    waiting_for_game_message,
)


@dataclass(frozen=True, unsafe_hash=False)
class BackgroundAiogramGameMessageSending(GameMessageSending):
    _tasks: BackgroundTasks
    _bot: Bot

    async def send_messages(
        self, messages: Sequence[GameMessage], /,
    ) -> None:
        await gather(*(self.send_message(message) for message in messages))

    async def send_message(
        self, message: GameMessage, /,
    ) -> None:
        match message:
            case PlayerAlreadyInGameMessage(PlayerLocation(chat_id=chat_id)):
                self._tasks.create_task(
                    player_already_in_game_message(self._bot, chat_id),
                )

            case WaitingForGameMessage(PlayerLocation(chat_id=chat_id)):
                self._tasks.create_task(
                    waiting_for_game_message(self._bot, chat_id),
                )
            case DoubleWaitingForGameMessage(PlayerLocation(chat_id=chat_id)):
                self._tasks.create_task(
                    double_waiting_for_game_message(self._bot, chat_id),
                )
