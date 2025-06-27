from collections.abc import Sequence

from aiogram.types.message import Message
from aiogram.utils.formatting import Bold, Text, as_list


async def profile_message(  # noqa: PLR0913, PLR0917
    message: Message,
    stars: int,
    emojis: Sequence[str],
    selected_emoji: str | None,
    number_of_wins: int,
    number_of_draws: int,
    number_of_defeats: int,
    is_in_game: bool,  # noqa: FBT001
) -> None:
    total = number_of_wins + number_of_defeats + number_of_draws

    if total > 0:
        winning_percentage = number_of_wins / total * 100
        winning_percentage_text = (
            f"{int(winning_percentage)}"
            if int(winning_percentage) == winning_percentage
            else f"{winning_percentage:.2f}"
        )
    else:
        winning_percentage_text = None

    if emojis:
        emoji_value_texts = (
            Text(Bold("<", selected_emoji, ">"))
            if emoji == selected_emoji
            else Text(emoji)
            for emoji in emojis
        )
        emoji_text_values = as_list(emoji_value_texts, sep="")

        preview_emoji = "🎭" if selected_emoji is None else selected_emoji
        emoji_texts = [Text(f"{preview_emoji} Эмоджи: ", emoji_text_values)]
    else:
        emoji_texts = []

    content = as_list(
        f"🌟 Звёзд: {stars}",
        f"🏆 Побед: {number_of_wins}",
        f"💀 Поражений: {number_of_defeats}",
        f"🕊️ Ничьих: {number_of_draws}",
        *emoji_texts,
        *(
            []
            if winning_percentage_text is None
            else [f"📊 Процент побед: {winning_percentage_text}%"]
        ),
        "⚔️ Сейчас в игре" if is_in_game else "💤 Сейчас не в игре",
    )
    await message.answer(**content.as_kwargs())
