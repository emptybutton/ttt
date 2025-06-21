import re

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from ttt.application.common.ports.players import NoPlayerWithIDError
from ttt.application.game.make_move_in_game import MakeMoveInGame
from ttt.application.game.wait_game import WaitGame
from ttt.entities.core.game.cell import AlreadyFilledCellError
from ttt.entities.core.game.game import (
    CompletedGameError,
    NoCellError,
    NotCurrentPlayerError,
)
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram.common.messages import anons_are_rohibited_message
from ttt.presentation.aiogram.game.messages import (
    already_completed_game_message,
    already_filled_cell_message,
    invalid_board_position_message,
    no_cell_message,
    not_current_player_message,
)


class GameViewState(StatesGroup):
    waiting_game = State()
    waiting_move = State()


game_router = Router(name=__name__)


@game_router.message(StateFilter(None), Command("game"))
@inject
async def wait_game_route(
    message: Message,
    wait_game: FromDishka[WaitGame],
    state: FSMContext,
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(message)
        return

    await wait_game(PlayerLocation(message.from_user.id, message.chat.id))
    await state.set_state(GameViewState.waiting_game)


@game_router.message(StateFilter(GameViewState.waiting_move))
@inject
async def make_move_in_game_route(
    message: Message,
    make_move_in_game: FromDishka[MakeMoveInGame],
    state: FSMContext,
) -> None:
    if message.from_user is None:
        await anons_are_rohibited_message(message)
        return

    text = not_none(message.text)
    pattern = r"^-?\d+\s-?\d+$"
    is_format_valid = bool(re.match(pattern, text))

    if not is_format_valid:
        await invalid_board_position_message(
            not_none(message.bot), message.chat.id,
        )
        return

    x, y = map(int, text.split()[:2])

    try:
        result = await make_move_in_game(
            PlayerLocation(message.from_user.id, message.chat.id), (x, y),
        )
    except NoPlayerWithIDError:
        await anons_are_rohibited_message(message)
    except CompletedGameError:
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
    else:
        if result is not None:
            await state.clear()
