from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.game.cancel_game import CancelGame
from ttt.entities.core.player.location import PlayerLocation
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message


cancel_game_router = Router(name=__name__)


@cancel_game_router.message(Command("cancel_game"))
@inject
async def _(
    message: Message,
    cancel_game: FromDishka[CancelGame],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(message)
        return

    await cancel_game(PlayerLocation(message.from_user.id, message.chat.id))
