from aiogram.client.bot import Bot
from aiogram.enums import ParseMode
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.formatting import Bold, BotCommand, Text, as_list

from ttt.entities.core.game.game import Game, GameState
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.game.keyboards import game_keyboard
from ttt.presentation.aiogram.game.texts import game_cell


async def started_game_message(
    bot: Bot,
    chat_id: int,
    game: Game,
    player_id: int,
) -> None:
    if player_id == game.player1.id:
        about_players = (
            f"Вы — {game.player1_emoji.str_}, враг — {game.player2_emoji.str_}"
        )
        about_move = "Ходите"
    else:
        about_players = (
            f"Враг — {game.player1_emoji.str_}, вы — {game.player2_emoji.str_}"
        )
        about_move = "Ждите хода врага"

    content = as_list(
        "⚔️ Игра началась",
        about_players,
        about_move,
    )
    await bot.send_message(
        chat_id, **content.as_kwargs(), reply_markup=game_keyboard(game),
    )


async def maked_move_message(
    bot: Bot,
    chat_id: int,
    game: Game,
    player_id: int,
) -> None:
    match player_id, game.state:
        case (
            (game.player1.id, GameState.wait_player1)
            | (game.player2.id, GameState.wait_player2)
        ):
            message = "🎯 Ходите"
        case (
            (game.player2.id, GameState.wait_player1)
            | (game.player1.id, GameState.wait_player2)
        ):
            message = "🎯 Ждите хода врага"
        case _:
            raise ValueError(game.state, player_id)

    keyboard = game_keyboard(game)
    await bot.send_message(chat_id, message, reply_markup=keyboard)


async def completed_game_message(
    bot: Bot,
    chat_id: int,
    game: Game,
    player_id: int,
) -> None:
    result = not_none(game.result)

    match result.winner_id:
        case int() if result.winner_id == player_id:
            result_emoji = "🎆"
            about_result = "Вы победили!"
        case None:
            result_emoji = "🕊"
            about_result = "Ничья!"
        case _:
            result_emoji = "💀"
            about_result = "Вы проиграли!"

    board_content = as_list(*(
        as_list(*(game_cell(cell, game, " ") for cell in line), sep="")
        for line in game.board
    ))
    content = as_list(about_result, board_content, sep="\n\n")

    await bot.send_message(chat_id, result_emoji)
    await bot.send_message(
        chat_id,
        **content.as_kwargs(),
        reply_markup=ReplyKeyboardRemove(),
    )


async def player_already_in_game_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "⚔️ Вы уже в игре")


async def waiting_for_game_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "👥 Поиск игры начат")


async def double_waiting_for_game_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "👥 Поиск игры уже начат")


async def no_game_message(bot: Bot, chat_id: int) -> None:
    text = Text("❌ Игры нет. Для поиска введите: ", Bold(BotCommand("game")))
    await bot.send_message(chat_id, **text.as_kwargs())


async def already_completed_game_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "❌ Игра уже завершилась")


async def not_current_player_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "❌ Сейчас не ваш ход")


async def no_cell_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "❌ Такой ячейки нет")


async def already_filled_cell_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "❌ Ячейка уже проставлена")
