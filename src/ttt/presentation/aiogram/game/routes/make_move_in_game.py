
from aiogram import F, Router
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.common.ports.players import NoPlayerWithIDError
from ttt.application.game.make_move_in_game import MakeMoveInGame
from ttt.application.game.ports.games import NoGameError
from ttt.entities.core.game.cell import AlreadyFilledCellError
from ttt.entities.core.game.game import (
    AlreadyCompletedGameError,
    NoCellError,
    NotCurrentPlayerError,
)
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.messages import (
    anons_are_rohibited_message,
    need_to_start_message,
)
from ttt.presentation.aiogram.game.messages import (
    already_completed_game_message,
    already_filled_cell_message,
    no_cell_message,
    no_game_message,
    not_current_player_message,
)


make_move_in_game_router = Router(name=__name__)


@make_move_in_game_router.message(F.text.regexp(r"^-?\d+\s-?\d+$"))
@inject
async def _(
    message: Message,
    make_move_in_game: FromDishka[MakeMoveInGame],
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(message)
        return

    x, y = map(int, not_none(message.text).split()[:2])
    x -= 1
    y -= 1

    try:
        await make_move_in_game(
            PlayerLocation(message.from_user.id, message.chat.id), (x, y),
        )
    except NoPlayerWithIDError:
        await need_to_start_message(message)
    except NoGameError:
        await no_game_message(not_none(message.bot), message.chat.id)
    except AlreadyCompletedGameError:
        await already_completed_game_message(
            not_none(message.bot), message.chat.id,
        )
    except NotCurrentPlayerError:
        await not_current_player_message(not_none(message.bot), message.chat.id)
    except NoCellError:
        await no_cell_message(not_none(message.bot), message.chat.id)
    except AlreadyFilledCellError:
        await already_filled_cell_message(
            not_none(message.bot), message.chat.id,
        )
