from collections.abc import Sequence

from aiogram.utils.formatting import Bold, Text, as_list


def emoji_list_text(
    emojis: Sequence[str],
    selected_emoji: str | None,
) -> Text | None:
    if not emojis:
        return None

    emoji_value_texts = (
        Text(Bold("<", selected_emoji, ">"))
        if emoji == selected_emoji
        else Text(emoji)
        for emoji in emojis
    )
    return as_list(*emoji_value_texts, sep=" ")
