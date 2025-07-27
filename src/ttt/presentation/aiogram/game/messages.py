from aiogram.client.bot import Bot
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.formatting import Bold, Text, Underline, as_list

from ttt.entities.core.game.game import (
    Game,
    GameState,
)
from ttt.entities.core.game.game_result import (
    CancelledGameResult,
    DecidedGameResult,
    DrawGameResult,
)
from ttt.entities.core.user.draw import UserDraw
from ttt.entities.core.user.loss import UserLoss
from ttt.entities.core.user.win import UserWin
from ttt.presentation.aiogram.common.texts import (
    copy_signed_text,
    short_float_text,
)
from ttt.presentation.aiogram.game.keyboards import (
    game_keyboard,
    keyboard_to_start_game_with_ai,
)
from ttt.presentation.aiogram.game.texts import game_cell


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
    if user_id == game.player1.id:
        about_users = Text(
            Underline("Вы"),
            f" — {game.player1_emoji.str_}",
            f", Враг — {game.player2_emoji.str_}",
        )
        about_move = "Ходите"
    else:
        about_users = Text(
            f"Враг — {game.player1_emoji.str_}, ",
            Underline("Вы"),
            f" — {game.player2_emoji.str_}",
        )
        about_move = "Ждите хода врага"

    content = as_list(
        "⚔️ Игра началась",
        about_users,
        about_move,
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
    match user_id, game.state:
        case (game.player1.id, GameState.wait_player1) | (
            game.player2.id,
            GameState.wait_player2,
        ):
            message = "🎯 Ходите"
        case (game.player2.id, GameState.wait_player1) | (
            game.player1.id,
            GameState.wait_player2,
        ):
            message = "🎯 Ждите хода врага"
        case _:
            raise ValueError(game.state, user_id)

    keyboard = game_keyboard(game)
    await bot.send_message(chat_id, message, reply_markup=keyboard)


async def completed_game_messages(
    bot: Bot,
    chat_id: int,
    game: Game,
    user_id: int,
) -> None:
    match game.result:
        case DecidedGameResult(win=UserWin(
            user_id=winner_id, new_stars=None, rating_vector=None,
        )) if winner_id == user_id:
            result_emoji = "🎆"
            about_result = Text("Вы победили!")
        case DecidedGameResult(win=UserWin(
            user_id=winner_id,
            new_stars=int() as new_stars,
            rating_vector=float() as rating_vector,
        )) if winner_id == user_id:
            result_emoji = "🎆"
            rating_value_text = copy_signed_text(
                short_float_text(rating_vector),
                rating_vector,
            )
            about_result = as_list(
                "Вы победили!",
                f"+{new_stars} 🌟",
                f"{rating_value_text} 🏅",
                sep="\n",
            )
        case DecidedGameResult(loss=UserLoss(
            user_id=loser_id,
            rating_vector=float() as rating_vector,
        )) if loser_id == user_id:
            result_emoji = "💀"
            rating_value_text = copy_signed_text(
                short_float_text(rating_vector),
                rating_vector,
            )
            about_result = as_list(
                "Вы проиграли!",
                f"{rating_value_text} 🏅",
                sep="\n",
            )
        case DecidedGameResult(loss=UserLoss(
            user_id=loser_id,
            rating_vector=None,
        )) if loser_id == user_id:
            result_emoji = "💀"
            about_result = Text("Вы проиграли!")
        case DrawGameResult(draw1, draw2):
            if isinstance(draw1, UserDraw) and draw1.user_id == user_id:
                user_draw = draw1
            elif isinstance(draw2, UserDraw) and draw2.user_id == user_id:
                user_draw = draw2
            else:
                raise ValueError

            if user_draw.rating_vector is not None:
                rating_vector_value_text = copy_signed_text(
                    short_float_text(user_draw.rating_vector),
                    user_draw.rating_vector,
                )
                rating_vector_text = f"{rating_vector_value_text} 🏅"
            else:
                rating_vector_text = None

            result_emoji = "🕊"
            about_result = as_list(
                "Ничья!",
                *([] if rating_vector_text is None else [rating_vector_text]),
            )
        case CancelledGameResult():
            result_emoji = "👻"
            about_result = Text("Игра отменена!")
        case _:
            raise ValueError

    board_content = as_list(
        *(
            as_list(*(game_cell(cell, game, "░░") for cell in line), sep="░░")
            for line in game.board
        ),
        sep="\n░░░░░░░░░░\n",
    )

    content = as_list(about_result, board_content, sep="\n\n")

    await bot.send_message(chat_id, result_emoji)
    await bot.send_message(
        chat_id,
        **content.as_kwargs(),
        reply_markup=ReplyKeyboardRemove(),
    )


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
