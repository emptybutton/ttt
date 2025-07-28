from aiogram.utils.formatting import Text, Underline

from ttt.entities.core.game.cell import Cell
from ttt.entities.core.game.game import Game, GameState


def game_cell(
    cell: Cell,
    game: Game,
    default: str,
) -> str:
    match cell.filler_id():
        case game.player1.id:
            return game.player1_emoji.str_
        case game.player2.id:
            return game.player2_emoji.str_
        case None:
            return default
        case _:
            raise ValueError((cell.filler_id, game.player1.id, game.player2.id))


def move_hint_text_with_emoji(game: Game, user_id: int) -> str:
    match user_id, game.state:
        case (game.player1.id, GameState.wait_player1) | (
            game.player2.id,
            GameState.wait_player2,
        ):
            return "🎯 Ходите"
        case (game.player2.id, GameState.wait_player1) | (
            game.player1.id,
            GameState.wait_player2,
        ):
            return "🎯 Ждите хода врага"
        case _:
            raise ValueError(game.state, user_id)


def move_hint_text_without_emoji(game: Game, user_id: int) -> str:
    match user_id, game.state:
        case (game.player1.id, GameState.wait_player1) | (
            game.player2.id,
            GameState.wait_player2,
        ):
            return "Ходите"
        case (game.player2.id, GameState.wait_player1) | (
            game.player1.id,
            GameState.wait_player2,
        ):
            return "Ждите хода врага"
        case _:
            raise ValueError(game.state, user_id)


def player_order_text(game: Game, user_id: int) -> Text:
    if user_id == game.player1.id:
        return Text(
            Underline("Вы"),
            f" — {game.player1_emoji.str_}",
            f", Враг — {game.player2_emoji.str_}",
        )

    return Text(
        f"Враг — {game.player1_emoji.str_}, ",
        Underline("Вы"),
        f" — {game.player2_emoji.str_}",
    )
