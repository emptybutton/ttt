from aiogram.client.bot import Bot
from aiogram.utils.formatting import Bold, Text, as_list

from ttt.entities.core.game.game import (
    Game,
)
from ttt.entities.core.game.game_result import (
    CancelledGameResult,
    DecidedGameResult,
    DrawGameResult,
)
from ttt.entities.core.user.draw import UserDraw
from ttt.entities.core.user.loss import UserLoss
from ttt.entities.core.user.win import UserWin
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.texts import (
    copy_signed_text,
    short_float_text,
)
from ttt.presentation.aiogram.game.keyboards import (
    game_keyboard,
    keyboard_to_select_game_mode,
    keyboard_to_start_game_with_ai,
)
from ttt.presentation.aiogram.game.texts import (
    game_cell,
    move_hint_text_with_emoji,
    move_hint_text_without_emoji,
    player_order_text,
)
from ttt.presentation.aiogram.user.keyboards import main_menu_keyboard


async def game_modes_to_get_started_message(
    bot: Bot,
    chat_id: int,
) -> None:
    text = Text("⚔️ Выберите режим игры")
    keyboard = keyboard_to_select_game_mode()

    await bot.send_message(
        chat_id,
        **text.as_kwargs(),
        reply_markup=keyboard,
    )


async def message_to_start_game_with_ai(
    bot: Bot,
    chat_id: int,
) -> None:
    text = Text("🤖 Выберите тип ИИ")
    keyboard = keyboard_to_start_game_with_ai()

    await bot.send_message(
        chat_id,
        **text.as_kwargs(),
        reply_markup=keyboard,
    )


async def started_game_message(
    bot: Bot,
    chat_id: int,
    game: Game,
    user_id: int,
) -> None:
    player_order_text_ = player_order_text(game, user_id)
    move_hint_text = move_hint_text_without_emoji(game, user_id)

    content = as_list(
        "⚔️ Игра началась",
        player_order_text_,
        move_hint_text,
    )
    await bot.send_message(
        chat_id,
        **content.as_kwargs(),
        reply_markup=game_keyboard(game),
    )


async def maked_move_message(
    bot: Bot,
    chat_id: int,
    game: Game,
    user_id: int,
) -> None:
    message = move_hint_text_with_emoji(game, user_id)

    keyboard = game_keyboard(game)
    await bot.send_message(chat_id, message, reply_markup=keyboard)


async def game_message(
    bot: Bot,
    chat_id: int,
    game: Game,
    user_id: int,
) -> None:
    content = as_list(
        player_order_text(game, user_id),
        move_hint_text_without_emoji(game, user_id),
    )

    await bot.send_message(
        chat_id, **content.as_kwargs(), reply_markup=game_keyboard(game),
    )


async def completed_game_message(
    bot: Bot,
    chat_id: int,
    game: Game,
    user_id: int,
) -> None:
    match game.result:
        case DecidedGameResult(win=UserWin(winner_id)) if winner_id == user_id:
            result_emoji = "🎆"
        case DecidedGameResult(loss=UserLoss(loser_id)) if loser_id == user_id:
            result_emoji = "💀"
        case DrawGameResult():
            result_emoji = "🕊"
        case CancelledGameResult():
            result_emoji = "👻"
        case _:
            raise ValueError

    await bot.send_message(chat_id, result_emoji)


async def user_already_in_game_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "⚔️ Вы уже в игре")


async def waiting_for_game_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "👥 Поиск игры начат")


async def double_waiting_for_game_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "👥 Поиск игры уже начат")


async def no_game_message(bot: Bot, chat_id: int) -> None:
    text = Text(
        "❌ Игры нет. Чтобы начать введите ",
        Bold("/game"),
        " или ",
        Bold("/game_with_ai"),
    )
    await bot.send_message(chat_id, **text.as_kwargs())


async def already_completed_game_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "❌ Игра уже завершилась")


async def not_current_user_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "❌ Сейчас не ваш ход")


async def no_cell_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "❌ Такой ячейки нет")


async def already_filled_cell_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "❌ Ячейка уже проставлена")
