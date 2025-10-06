from dataclasses import dataclass
from uuid import UUID

from ttt.application.game.game.ports.game_tasks import GameTasks
from ttt.infrastructure.remote_funcs.make_ai_move_in_game import (
    make_ai_move_in_game_remotely,
)


@dataclass
class NatsRemoteFuncGameTasks(GameTasks):
    async def make_ai_move(
        self,
        user_id: int,
        game_id: UUID,
        ai_id: UUID,
        /,
    ) -> None:
        await make_ai_move_in_game_remotely(
            user_id=user_id, game_id=game_id.hex, ai_id=ai_id.hex,
        )
