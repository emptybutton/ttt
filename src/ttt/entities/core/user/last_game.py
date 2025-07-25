from dataclasses import dataclass
from uuid import UUID

from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True)
class LastGame:
    id: UUID
    user_id: int
    game_id: UUID


def last_game(
    last_game_id: UUID,
    last_game_user_id: int,
    last_game_game_id: UUID,
    tracking: Tracking,
) -> LastGame:
    last_game = LastGame(last_game_id, last_game_user_id, last_game_game_id)
    tracking.register_new(last_game)

    return last_game
