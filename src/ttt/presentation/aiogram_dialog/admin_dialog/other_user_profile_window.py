from dataclasses import dataclass

from aiogram.enums import ContentType
from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from magic_filter import F

from ttt.application.user.view_other_user import ViewOtherUser
from ttt.entities.core.user.rank import rank_for_rating
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram_dialog.admin_dialog.common import AdminDialogState
from ttt.presentation.aiogram_dialog.common.data import EncodableToWindowData
from ttt.presentation.aiogram_dialog.common.wigets.one_time_key import (
    OneTimekey,
)
from ttt.presentation.texts import (
    rank_title,
    short_float_text,
)


@dataclass(frozen=True)
class OtherUserProfileView(EncodableToWindowData):
    id_: int
    number_of_wins: int
    number_of_draws: int
    number_of_defeats: int
    account_stars: int
    rating_text: str
    rank_text: str

    def _data_key(self) -> str:
        return "profile"

    @classmethod
    def of(  # noqa: PLR0913, PLR0917
        cls,
        id_: int,
        number_of_wins: int,
        number_of_draws: int,
        number_of_defeats: int,
        account_stars: int,
        rating: float,
    ) -> "OtherUserProfileView":
        return OtherUserProfileView(
            id_=id_,
            number_of_wins=number_of_wins,
            number_of_draws=number_of_draws,
            number_of_defeats=number_of_defeats,
            account_stars=account_stars,
            rating_text=short_float_text(rating),
            rank_text=rank_title(rank_for_rating(rating)),
        )


@inject
async def input_user_id(
    message: Message,
    _: MessageInput,
    manager: DialogManager,
    view_other_user: FromDishka[ViewOtherUser],
) -> None:
    try:
        other_user_id = int(message.text)  # type: ignore[arg-type]
    except ValueError:
        await manager.start(
            AdminDialogState.other_user_profile,
            {"hint": "❌ ID должен быть целочисленым числом:"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )
    else:
        await view_other_user(not_none(message.from_user).id, other_user_id)


other_user_profile_window = Window(
    Format("{start_data[hint]}", when=F["start_data"]["hint"]),

    Const(
        "🎭 Введите ID пользователя:",
        when=~F["start_data"]["profile"] & ~F["start_data"]["hint"],
    ),
    MessageInput(
        input_user_id,
        content_types=[ContentType.ANY],
    ),

    Multi(
        Format("🎭 Профиль пользователя {start_data[profile][id_]}"),
        Const(" "),
        Format("🌟 Звёзд: {start_data[profile][account_stars]}"),
        Format("🏅 Рейтинг: {start_data[profile][rating_text]}"),
        Format("⚔️ Ранг: {start_data[profile][rank_text]}"),
        Format("🏆 Побед: {start_data[profile][number_of_wins]}"),
        Format("💀 Поражений: {start_data[profile][number_of_defeats]}"),
        Format("🕊️ Ничьих: {start_data[profile][number_of_draws]}"),
        when=F["start_data"]["profile"] & ~F["start_data"]["hint"],
    ),
    SwitchTo(Const("Назад"), id="back", state=AdminDialogState.main),

    OneTimekey("profile"),
    OneTimekey("hint"),
    state=AdminDialogState.other_user_profile,
)
