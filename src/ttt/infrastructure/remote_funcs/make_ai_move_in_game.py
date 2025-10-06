from uuid import UUID

from dishka import AsyncContainer

from ttt.application.game.game.make_ai_move_in_game import MakeAiMoveInGame
from ttt.infrastructure.remote_funcs.nats_remote_func import nats_remote
from ttt.infrastructure.retrier import Retrier


@nats_remote(
    subject="game.game.make_ai_move_in_game",
    pull_subscribe=lambda js, subject: js.pull_subscribe(
        subject,
        durable="ttt-game-game-make_ai_move_in_game",
        stream="GAME",
    ),
)
async def make_ai_move_in_game_remotely(
    container: AsyncContainer,
    *,
    user_id: int,
    game_id: str,
    ai_id: str,
) -> None:
    retrier = await container.get(Retrier)
    make_ai_move_in_game = await container.get(MakeAiMoveInGame)

    await retrier(
        make_ai_move_in_game, user_id, UUID(hex=game_id), UUID(hex=ai_id),
    )
