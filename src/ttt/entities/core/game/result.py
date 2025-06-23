from dataclasses import dataclass
from uuid import UUID

from ttt.entities.core.player.win import Win


@dataclass(frozen=True)
class GameResult:
    id: UUID
    game_id: UUID
    win: Win | None
