from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.state import any_state
from aiogram.types import Message
from aiogram_dialog import (
    DialogManager,
    StartMode,
)
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.user.register_user import RegisterUser
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.fsm import CommonState
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message


start_router = Router(name=__name__)


@start_router.message(any_state, Command("start"))
@inject
async def _(
    message: Message,
    register_user: FromDishka[RegisterUser],
    dialog_manager: DialogManager,
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(
            not_none(message.bot),
            message.chat.id,
        )
        return

    await register_user(message.from_user.id)
    await dialog_manager.start(CommonState.main, mode=StartMode.RESET_STACK)
