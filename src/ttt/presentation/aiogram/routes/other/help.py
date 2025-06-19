from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.player.register_player import RegisterPlayer
from ttt.presentation.aiogram.messages.command import help_message
from ttt.presentation.aiogram.messages.common import anons_are_rohibited_message


help_router = Router(name=__name__)


@help_router.message(Command("help"))
async def help(message: Message) -> None:
    await help_message(message)
