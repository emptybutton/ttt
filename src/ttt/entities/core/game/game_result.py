from dataclasses import dataclass

from ttt.entities.core.game.player_result import (
    PlayerDraw,
    PlayerLoss,
    PlayerWin,
)


@dataclass(frozen=True)
class DecidedGameResult:
    win: PlayerWin
    lose: PlayerLoss


@dataclass(frozen=True)
class DrawGameResult:
    draw1: PlayerDraw
    draw2: PlayerDraw


@dataclass(frozen=True)
class CancelledGameResult:
    canceler_id: int


type GameResult = DecidedGameResult | DrawGameResult | CancelledGameResult
