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
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState


start_router = Router(name=__name__)


@start_router.message(any_state, Command("start"))
@inject
async def _(
    message: Message,
    register_user: FromDishka[RegisterUser],
    dialog_manager: DialogManager,
) -> None:
    if message.from_user is None:
        return

    await register_user(message.from_user.id)
    await dialog_manager.start(MainDialogState.main, mode=StartMode.RESET_STACK)
