from dataclasses import dataclass
from typing import Literal

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    Button,
    Group,
    Row,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Case, Const, Format, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from magic_filter import F

from ttt.application.game.game.make_move_in_game import MakeMoveInGame
from ttt.entities.core.game.cell_number import CellNumber
from ttt.entities.core.game.game import Game
from ttt.entities.core.game.game_result import (
    CancelledGameResult,
    DecidedGameResult,
    DrawGameResult,
)
from ttt.entities.core.user.draw import UserDraw
from ttt.entities.core.user.loss import UserLoss
from ttt.entities.core.user.win import UserWin
from ttt.entities.tools.assertion import not_none
from ttt.presentation.aiogram_dialog.common.data import EncodableToWindowData
from ttt.presentation.aiogram_dialog.common.wigets.one_time_key import (
    OneTimekey,
)
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState
from ttt.presentation.texts import (
    copy_signed_text,
    short_float_text,
)


@inject
async def on_cell_clicked(
    callback: CallbackQuery,
    button: Button,
    _: DialogManager,
    make_move_in_game: FromDishka[MakeMoveInGame],
) -> None:
    cell_number_int = int(not_none(button.widget_id)[-1])
    await make_move_in_game(callback.from_user.id, cell_number_int)


def cell_button(cell_number_int: int) -> Button:
    return Button(
        Format(
            "{start_data[active_game][cell_view_by_cell_number_int]"
            f"[_{cell_number_int}]"
            "}",
        ),
        id=f"game_cell_{cell_number_int}",
        on_click=on_cell_clicked,
    )


@dataclass(frozen=True)
class ActiveGameView(EncodableToWindowData):
    is_current_players_move_expected: bool
    cell_view_by_cell_number_int: dict[str, str]
    is_user_player1: bool
    player1_emoji: str
    player2_emoji: str

    def _data_key(self) -> str:
        return "active_game"

    @classmethod
    def of(cls, game: Game, user_id: int) -> "ActiveGameView":
        cell_view_by_cell_number_int = dict[str, str]()

        for cell_number_int in range(1, 10):
            cell_number = CellNumber(cell_number_int)
            cell_emoji_ = game.cell_emoji(cell_number.board_position())

            cell_view = " " if cell_emoji_ is None else cell_emoji_.str_
            cell_view_by_cell_number_int[f"_{cell_number_int}"] = cell_view

        return ActiveGameView(
            is_current_players_move_expected=game.is_player_move_expected(
                user_id,
            ),
            cell_view_by_cell_number_int=cell_view_by_cell_number_int,
            is_user_player1=game.player1.id == user_id,
            player1_emoji=game.player1_emoji.str_,
            player2_emoji=game.player2_emoji.str_,
        )


type CompletedGameViewType = Literal["win", "loss", "draw", "cancelled_game"]


@dataclass(frozen=True)
class CompletedGameView(EncodableToWindowData):
    type_: CompletedGameViewType
    rating_vector_text: str | None
    new_stars: int | None
    cell_view_by_number: dict[str, str]

    def _data_key(self) -> str:
        return "completed_game"

    @classmethod
    def of(cls, game: Game, user_id: int) -> "CompletedGameView":
        type_: CompletedGameViewType

        match game.result:
            case DecidedGameResult(
                win=UserWin(user_id=winner_id) as win,
            ) if winner_id == user_id:
                type_ = "win"
                rating_vector = win.rating_vector
                new_stars = win.new_stars

            case DecidedGameResult(
                loss=UserLoss(user_id=loser_id) as loss,
            ) if loser_id == user_id:
                type_ = "loss"
                rating_vector = loss.rating_vector
                new_stars = None

            case DrawGameResult(draw1, draw2):
                if isinstance(draw1, UserDraw) and draw1.user_id == user_id:
                    draw = draw1
                elif isinstance(draw2, UserDraw) and draw2.user_id == user_id:
                    draw = draw2
                else:
                    raise ValueError

                type_ = "draw"
                rating_vector = draw.rating_vector
                new_stars = None

            case CancelledGameResult():
                type_ = "cancelled_game"
                rating_vector = None
                new_stars = None

            case _:
                raise ValueError

        if rating_vector is None:
            rating_vector_text = None
        else:
            rating_vector_text = copy_signed_text(
                short_float_text(rating_vector), rating_vector,
            )

        cell_emoji_by_number = {
            CellNumber.of_board_position((x, y)): game.cell_emoji((x, y))
            for x in range(3)
            for y in range(3)
        }
        cell_view_by_number = {
            f"_{(int(number))}": "░░" if emoji is None else emoji.str_
            for number, emoji in cell_emoji_by_number.items()
        }

        return CompletedGameView(
            type_=type_,
            rating_vector_text=rating_vector_text,
            new_stars=new_stars,
            cell_view_by_number=cell_view_by_number,
        )


active_game_f = F["start_data"]["active_game"]

completed_game_f = F["start_data"]["completed_game"]
rating_f = completed_game_f["rating_vector_text"].is_not(None)
stars_f = completed_game_f["new_stars"].is_not(None)

game_window = Window(
    Case(selector=active_game_f["is_user_player1"], when=active_game_f, texts={
        True: Format(
            "Вы — {start_data[active_game][player1_emoji]}"
            ", Враг — {start_data[active_game][player2_emoji]}",
        ),
        False: Format(
            "Враг — {start_data[active_game][player1_emoji]}"
            ", Вы — {start_data[active_game][player2_emoji]}",
        ),
    }),
    Case(
        selector=active_game_f["is_current_players_move_expected"],
        when=active_game_f,
        texts={
            True: Const("Ходите"),
            False: Const("Ждите хода врага"),
        },
    ),
    Multi(
        Const(" "),
        Format("{start_data[hint]}"),
        when=active_game_f & F["start_data"]["hint"],
    ),

    Group(
        Row(cell_button(1), cell_button(2), cell_button(3)),
        Row(cell_button(4), cell_button(5), cell_button(6)),
        Row(cell_button(7), cell_button(8), cell_button(9)),
        when=active_game_f,
    ),

    Multi(
        Case(
            selector=completed_game_f["type_"],
            texts={
                "win": Const("Вы победили!"),
                "loss": Const("Вы проиграли!"),
                "draw": Const("Ничья!"),
                "cancelled_game": Const("Игра отменена!"),
            },
        ),

        Const(" ", when=(rating_f | stars_f)),
        Format(
            "{start_data[completed_game][rating_vector_text]} 🏅",
            when=rating_f,
        ),
        Format("+{start_data[completed_game][new_stars]} 🌟", when=stars_f),

        Const(" "),
        Format(
            "{start_data[completed_game][cell_view_by_number][_1]}"
            "░░{start_data[completed_game][cell_view_by_number][_2]}"
            "░░{start_data[completed_game][cell_view_by_number][_3]}",
        ),
        Const("░░░░░░░░░░"),
        Format(
            "{start_data[completed_game][cell_view_by_number][_4]}"
            "░░{start_data[completed_game][cell_view_by_number][_5]}"
            "░░{start_data[completed_game][cell_view_by_number][_6]}",
        ),
        Const("░░░░░░░░░░"),
        Format(
            "{start_data[completed_game][cell_view_by_number][_7]}"
            "░░{start_data[completed_game][cell_view_by_number][_8]}"
            "░░{start_data[completed_game][cell_view_by_number][_9]}",
        ),

        when=completed_game_f,
    ),

    SwitchTo(Const("Назад"), id="back", state=MainDialogState.main),
    OneTimekey("hint"),
    state=MainDialogState.game,
)
