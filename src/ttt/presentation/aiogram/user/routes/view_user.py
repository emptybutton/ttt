from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.state import any_state
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.user.view_user import ViewUser
from ttt.entities.core.user.location import UserLocation
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message


view_user_router = Router(name=__name__)


@view_user_router.message(any_state, Command("profile"))
@inject
async def _(
    message: Message,
    view_user: FromDishka[ViewUser],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(
            not_none(message.bot),
            message.chat.id,
        )
        return

    location = UserLocation(message.from_user.id, message.chat.id)
    await view_user(location)
