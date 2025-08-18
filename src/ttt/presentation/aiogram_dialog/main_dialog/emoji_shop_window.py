
from aiogram.enums import ContentType
from aiogram.types.message import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from magic_filter import F

from ttt.application.user.emoji_purchase.buy_emoji import BuyEmoji
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.user.parsing import parsed_emoji_str
from ttt.presentation.aiogram_dialog.common.wigets.hint import Hint
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState


@inject
async def handler(
    message: Message,
    _: MessageInput,
    __: DialogManager,
    buy_emoji: FromDishka[BuyEmoji],
) -> None:
    emoji_str = parsed_emoji_str(message)

    await buy_emoji(not_none(message.from_user).id, emoji_str)


emoji_shop_window = Window(
    Const("🎭 Введите эмоджи:", when=~F["start_data"]["hint"]),
    Hint(Format("{start_data[hint]}")),
    SwitchTo(Const("Назад"), id="back", state=MainDialogState.shop),
    MessageInput(handler, content_types=[ContentType.ANY]),
    state=MainDialogState.emoji_shop,
)
