from aiogram.methods import SendMessage
from aiogram.types.message import Message
from aiogram.utils.formatting import as_key_value, as_list


def player_info_message(
    message: Message,
    number_of_wins: int,
    number_of_draws: int,
    number_of_defeats: int,
    is_in_game: bool,  # noqa: FBT001
) -> SendMessage:
    total = number_of_wins + number_of_defeats + number_of_draws

    if total > 0:
        winning_percentage = number_of_wins / total * 100
        winning_percentage_text = f"{winning_percentage:.2f}"
    else:
        winning_percentage_text = None

    content = as_list(
        f"⭐ Побед: {number_of_wins}",
        f"💀 Поражений: {number_of_defeats}",
        f"🕊️ Ничьих: {number_of_draws}",
        *(
            []
            if winning_percentage_text is None
            else as_key_value("📊 Процент побед", winning_percentage_text)
        ),
        "",
        "⚔️ Сейчас в матче." if is_in_game else "💤 Сейчас не в матче",
    )
    return message.answer(**content.as_kwargs())
