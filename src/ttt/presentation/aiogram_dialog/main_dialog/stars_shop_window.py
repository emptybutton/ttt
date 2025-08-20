from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    Button,
    Row,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from magic_filter import F

from ttt.application.user.stars_purchase.start_stars_purchase import (
    StartStarsPurchase,
)
from ttt.presentation.aiogram_dialog.common.wigets.hint import Hint
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState


@inject
async def on_stars_purchase_clicked(
    callback: CallbackQuery,
    button: Button,
    _: DialogManager,
    start_stars_purchase: FromDishka[StartStarsPurchase],
) -> None:
    match button.widget_id:
        case "8192_stars_purchase":
            stars = 8192
        case "16384_stars_purchase":
            stars = 16384
        case "32768_stars_purchase":
            stars = 32768
        case "65536_stars_purchase":
            stars = 65536
        case _:
            raise ValueError(button.widget_id)

    await start_stars_purchase(callback.from_user.id, stars)


@inject
async def stars_shop_getter(  # noqa: RUF029
    *,
    dialog_manager: DialogManager,
    **_: Any,  # noqa: ANN401
) -> dict[str, Any]:
    return {
        "has_start_hint": (
            isinstance(dialog_manager.start_data, dict)
            and "hint" in dialog_manager.start_data
        ),
    }


stars_shop_window = Window(
    Const("🌟 Сколько звёзд хотите купить?", when=~F["start_data"]["hint"]),
    Row(
        Button(
            Const("8192 🌟 (128₽)"),
            id="8192_stars_purchase",
            on_click=on_stars_purchase_clicked,
        ),
        Button(
            Const("16384 🌟 (256₽)"),
            id="16384_stars_purchase",
            on_click=on_stars_purchase_clicked,
        ),
        when=~F["has_start_hint"],
    ),
    Row(
        Button(
            Const("32768 🌟 (512₽)"),
            id="32768_stars_purchase",
            on_click=on_stars_purchase_clicked,
        ),
        Button(
            Const("65536 🌟 (1024₽)"),
            id="65536_stars_purchase",
            on_click=on_stars_purchase_clicked,
        ),
        when=~F["has_start_hint"],
    ),

    Hint(Format("{start_data[hint]}")),

    SwitchTo(Const("Назад"), id="back", state=MainDialogState.shop),
    state=MainDialogState.stars_shop,
    getter=stars_shop_getter,
)
