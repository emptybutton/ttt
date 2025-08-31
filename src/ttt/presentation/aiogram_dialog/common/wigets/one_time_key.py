from typing import Any

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.text import Text


class OneTimekey(Text):
    def __init__(self, key: str) -> None:
        super().__init__(when=None)
        self.key = key

    async def _render_text(
            self, _: dict[str, Any], manager: DialogManager,
    ) -> str:
        if (
            isinstance(manager.start_data, dict)
            and self.key in manager.start_data
        ):
            del manager.start_data[self.key]

        return ""
