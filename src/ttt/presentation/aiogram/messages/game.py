from aiogram.client.bot import Bot
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.formatting import as_list

from ttt.entities.core.game.game import Game, GameState
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.keyboards.game import game_keyboard
from ttt.presentation.aiogram.text.game import game_cell, winner_emoji


async def started_game_message(
    bot: Bot,
    chat_id: int,
    game: Game,
    player_id: int,
) -> None:
    if player_id == game.player1.id:
        about_players = (
            f"Вы — {game.player1_emoji.char}, враг — {game.player2_emoji.char}"
        )
        about_move = "Ходите"
    else:
        about_players = (
            f"Враг — {game.player1_emoji.char}, вы — {game.player2_emoji.char}"
        )
        about_move = "Ждите хода врага"

    content = as_list(
        "⚔️ Матч начался",
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
            message = "🎯 Враг сделал свой ход. Ходите"
        case (
            (game.player2.id, GameState.wait_player1)
            | (game.player1.id, GameState.wait_player2)
        ):
            message = "🎯 Вы сделали свой ход. Ждите хода врага"
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
    winner_emoji_ = winner_emoji(game)

    match result.winner_id:
        case int() if result.winner_id == player_id:
            title = f"⭐️ Игра завершилась, вы — {winner_emoji_} победили!"
        case None:
            title = "🕊 Игра завершилась — ничья!"
        case _:
            title = f"💀 Игра завершилась, враг — {winner_emoji_} победил!"

    board_content = as_list(*(
        as_list(*(game_cell(cell, game, "�") for cell in line), sep=" ")
        for line in game.board
    ))
    content = as_list(title, board_content, sep="\n\n")

    await bot.send_message(
        chat_id,
        **content.as_kwargs(),
        reply_markup=ReplyKeyboardRemove(),
    )


async def player_already_in_game_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "⚔️ Вы уже в матче")


async def waiting_for_game_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "👥 Поиск игры начат")


async def invalid_board_position_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(
        chat_id,
        (
            "❌ Позиция ячейки — два числа, разделённые пробелом"
            ", но лучше используйте клавиатуру..."
        ),
    )


async def already_completed_game_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "❌ Игра уже завершилась")


async def not_current_player_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "❌ Сейчас не ваш ход")


async def no_cell_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "❌ Такой ячейки нет")


async def already_filled_cell_message(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, "❌ Ячейка уже проставлена")
