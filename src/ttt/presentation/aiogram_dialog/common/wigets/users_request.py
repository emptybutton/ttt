from collections.abc import Awaitable, Callable
from typing import Any

from aiogram.types import (
    CallbackQuery,
    KeyboardButton,
    KeyboardButtonRequestUsers,
)
from aiogram_dialog.api.internal import RawKeyboard
from aiogram_dialog.api.protocols import DialogManager, DialogProtocol
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.kbd import Keyboard
from aiogram_dialog.widgets.text import Text


UsersRequestOnClick = Callable[
    [CallbackQuery, "UsersRequest", DialogManager], Awaitable[Any],
]


class UsersRequest(Keyboard):
    def __init__(
        self,
        text: Text,
        id: str,  # noqa: A002
        criteria: KeyboardButtonRequestUsers,
        when: WhenCondition = None,
    ) -> None:
        super().__init__(id=id, when=when)
        self.text = text
        self.criteria = criteria

    async def _process_own_callback(
            self,
            callback: CallbackQuery,  # noqa: ARG002
            dialog: DialogProtocol,  # noqa: ARG002
            manager: DialogManager,  # noqa: ARG002
    ) -> bool:
        return True

    async def _render_keyboard(
            self,
            data: dict[Any, Any],
            manager: DialogManager,
    ) -> RawKeyboard:
        return [
            [
                KeyboardButton(
                    text=await self.text.render_text(data, manager),
                    request_users=self.criteria,
                ),
            ],
        ]
