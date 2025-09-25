from uuid import UUID

from dishka.integrations.taskiq import FromDishka, inject

from ttt.application.game.game.make_ai_move_in_game import MakeAiMoveInGame
from ttt.infrastructure.retrier import Retrier
from ttt.infrastructure.taskiq.broker import PullSubscribe
from ttt.infrastructure.taskiq.tasks.common import nats_tasks


@nats_tasks.task(
    task_name="game-game-make_ai_move_in_game",
    subject="game.game.make_ai_move_in_game",
    pull_subscribe=PullSubscribe(lambda js, subject: js.pull_subscribe(
        subject,
        durable="ttt-game-game-make_ai_move_in_game",
        stream="GAME",
    )),
)
@inject(patch_module=True)
async def make_ai_move_in_game_task(
    user_id: int,
    game_id: UUID,
    ai_id: UUID,
    make_ai_move_in_game: FromDishka[MakeAiMoveInGame],
    retrier: FromDishka[Retrier],
) -> None:
    await retrier(make_ai_move_in_game, user_id, game_id, ai_id)
