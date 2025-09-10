from collections.abc import Awaitable, Callable
from typing import Any

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.text import Text


class FuncText(Text):
    def __init__(
        self,
        func: Callable[[dict[str, Any], DialogManager], Awaitable[str]],
        *,
        when: WhenCondition = None,
    ) -> None:
        super().__init__(when=when)
        self.func = func

    async def _render_text(
        self,
        data: dict[str, Any],
        manager: DialogManager,
    ) -> str:
        return await self.func(data, manager)
