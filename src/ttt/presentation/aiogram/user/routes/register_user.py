from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.state import any_state
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.user.register_user import RegisterUser
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message


register_user_router = Router(name=__name__)


@register_user_router.message(any_state, Command("start"))
@inject
async def _(
    message: Message,
    register_user: FromDishka[RegisterUser],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(
            not_none(message.bot),
            message.chat.id,
        )
        return

    await register_user(message.from_user.id)
