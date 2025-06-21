from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import any_state
from aiogram.types import Message

from ttt.presentation.aiogram.messages.command import help_message


help_router = Router(name=__name__)


@help_router.message(Command("help"), any_state)
async def _(message: Message) -> None:
    await help_message(message)
