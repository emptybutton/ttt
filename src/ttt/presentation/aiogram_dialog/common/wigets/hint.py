from aiogram_dialog.widgets.text import Format
from magic_filter import F


def hint(key: str) -> Format:
    return Format(f"{{start_data[{key}]}}", when=F["start_data"][key])
