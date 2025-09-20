from dataclasses import dataclass
from typing import Any

from aiogram.types import User
from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import (
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from ttt.application.user.view_user import ViewUser
from ttt.entities.core.user.rank import UsersWithMaxRating, rank
from ttt.presentation.aiogram_dialog.common.data import EncodableToWindowData
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState
from ttt.presentation.result_buffer import ResultBuffer
from ttt.presentation.texts import (
    rank_title,
    short_float_text,
)


@dataclass(frozen=True)
class UserProfileView(EncodableToWindowData):
    number_of_wins: int
    number_of_draws: int
    number_of_defeats: int
    account_stars: int
    rating_text: str
    rank_text: str

    @classmethod
    def of(  # noqa: PLR0913, PLR0917
        cls,
        number_of_wins: int,
        number_of_draws: int,
        number_of_defeats: int,
        account_stars: int,
        rating: float,
        max_rating: float,
        users_with_max_rating: UsersWithMaxRating,
    ) -> "UserProfileView":
        return UserProfileView(
            number_of_wins=number_of_wins,
            number_of_draws=number_of_draws,
            number_of_defeats=number_of_defeats,
            account_stars=account_stars,
            rating_text=short_float_text(rating),
            rank_text=rank_title(
                rank(rating, max_rating, users_with_max_rating),
            ),
        )


@inject
async def profile_getter(
    *,
    event_from_user: User,
    view_user: FromDishka[ViewUser],
    result_buffer: FromDishka[ResultBuffer],
    **_: Any,  # noqa: ANN401
) -> dict[str, Any]:
    await view_user(event_from_user.id)
    view = result_buffer(UserProfileView)

    return view.window_data()


profile_window = Window(
    Multi(
        Const("🎭 Профиль"),
        Const(" "),
        Format("🌟 Звёзд: {main[account_stars]}"),
        Format("🏅 Рейтинг: {main[rating_text]}"),
        Format("⚔️ Ранг: {main[rank_text]}"),
        Format("🏆 Побед: {main[number_of_wins]}"),
        Format("💀 Поражений: {main[number_of_defeats]}"),
        Format("🕊️ Ничьих: {main[number_of_draws]}"),
    ),
    SwitchTo(Const("Назад"), id="back", state=MainDialogState.main),
    state=MainDialogState.profile,
    getter=profile_getter,
)
