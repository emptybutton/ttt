from uuid import UUID

from dishka.integrations.taskiq import FromDishka, inject

from ttt.application.game.game.make_ai_move_in_game import MakeAiMoveInGame
from ttt.infrastructure.retrier import Retrier
from ttt.infrastructure.taskiq.broker import NatsBroker


make_ai_move_in_game_broker = NatsBroker(
    "game.game.make_ai_move_in_game",
    lambda js, sub: js.pull_subscribe(
        sub, "ttt-game-game-make_ai_move_in_game", "GAME",
    ),
)


@make_ai_move_in_game_broker.task()
@inject(patch_module=True)
async def make_ai_move_in_game_broker_task(
    user_id: int,
    game_id: UUID,
    ai_id: UUID,
    make_ai_move_in_game: FromDishka[MakeAiMoveInGame],
    retrier: FromDishka[Retrier],
) -> None:
    await retrier(make_ai_move_in_game, user_id, game_id, ai_id)
