from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.game.game.ports.game_tasks import GameTasks
from ttt.infrastructure.sqlalchemy.tables.game import TableGame
from ttt.infrastructure.taskiq.tasks.make_ai_move_in_game_task import (
    make_ai_move_in_game_broker_task,
)


@dataclass
class TaskiqGameTasks(GameTasks):
    async def make_ai_move(
        self,
        user_id: int,
        game_id: UUID,
        ai_id: UUID,
        /,
    ) -> None:
        await make_ai_move_in_game_broker_task.kiq(user_id, game_id, ai_id)
