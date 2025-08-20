from typing import Any

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.text import Text
from magic_filter import F


class Hint(Text):
    def __init__(self, text: Text, hint_key: str = "hint") -> None:
        super().__init__(when=F["start_data"][hint_key])

        self.text = text
        self.hint_key = hint_key

    async def _render_text(
            self, data: dict[str, Any], manager: DialogManager,
    ) -> str:
        text = await self.text.render_text(data, manager)

        if isinstance(manager.start_data, dict):
            del manager.start_data[self.hint_key]

        return text
