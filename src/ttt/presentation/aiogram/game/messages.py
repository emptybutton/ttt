from aiogram.client.bot import Bot

from ttt.entities.core.game.game import (
    Game,
)
from ttt.entities.core.game.game_result import (
    CancelledGameResult,
    DecidedGameResult,
    DrawGameResult,
)
from ttt.entities.core.user.loss import UserLoss
from ttt.entities.core.user.win import UserWin


async def completed_game_sticker(
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
