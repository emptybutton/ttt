from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.state import any_state
from aiogram.types.message import Message
from aiogram_dialog import DialogManager, StartMode
from dishka.integrations.aiogram import inject

from ttt.presentation.aiogram_dialog.admin_dialog.common import AdminDialogState


admin_router = Router(name=__name__)


@admin_router.message(any_state, Command("admin"))
@inject
async def _(_: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(
        AdminDialogState.main, None, StartMode.RESET_STACK,
    )
