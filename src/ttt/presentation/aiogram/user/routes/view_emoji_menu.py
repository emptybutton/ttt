from aiogram import F, Router
from aiogram.filters import Command, or_f
from aiogram.fsm.state import any_state
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.user.view_emoji_menu import ViewEmojiMenu
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message


view_emoji_menu_router = Router(name=__name__)


@view_emoji_menu_router.message(
    any_state, or_f(Command("emoji_menu"), (F.text == "Эмоджи")),
)
@inject
async def _(
    message: Message,
    view_emoji_menu: FromDishka[ViewEmojiMenu],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(
            not_none(message.bot),
            message.chat.id,
        )
        return

    await view_emoji_menu(message.from_user.id)
