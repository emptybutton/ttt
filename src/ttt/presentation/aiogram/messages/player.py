from aiogram.methods import SendMessage
from aiogram.types.message import Message
from aiogram.utils.formatting import (
    Bold,
    as_key_value,
    as_list,
    as_marked_section,
)


def player_info_message(
    message: Message,
    number_of_wins: int,
    number_of_draws: int,
    number_of_defeats: int,
    is_in_game: bool,  # noqa: FBT001
) -> SendMessage:
    total = number_of_wins + number_of_defeats + number_of_draws
    winning_percentage = number_of_wins / total * 100

    content = as_list(
        as_marked_section(
            f"{Bold("Статистика"):}",
            as_key_value("Побед", number_of_wins),
            as_key_value("Поражений", number_of_defeats),
            as_key_value("Ничьих", number_of_draws),
            as_key_value("Процент побед", f"{winning_percentage:.2f}"),
            marker="  ",
        ),
        *(["Сейчас в партии."] if is_in_game else []),
        sep="\n\n",
    )
    return message.answer(**content.as_kwargs())
