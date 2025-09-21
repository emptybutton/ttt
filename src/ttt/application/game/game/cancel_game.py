from dataclasses import dataclass

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import SerializableTransaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.game.game.ports.game_log import GameLog
from ttt.application.game.game.ports.game_views import GameViews
from ttt.application.game.game.ports.games import Games
from ttt.entities.core.game.game import AlreadyCompletedGameError
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class CancelGame:
    map_: Map
    games: Games
    game_views: GameViews
    uuids: UUIDs
    transaction: SerializableTransaction
    log: GameLog

    async def __call__(self, user_id: int) -> None:
        """
        :raises ttt.application.common.errors.serialization_error.SerializationError:
        """  # noqa: E501

        async with self.transaction:
            game = await self.games.current_user_game(user_id)

            if game is None:
                await self.log.no_current_game_to_cancel_game(user_id)
                await self.transaction.commit()
                await self.game_views.no_current_game_view(user_id)
                return

            try:
                tracking = Tracking()
                game.cancel(user_id, tracking)
            except AlreadyCompletedGameError:
                await self.log.already_completed_game_to_cancel(game, user_id)
                await self.transaction.commit()
                await self.game_views.game_already_complteted_view(
                    user_id,
                    game,
                )
                return
            else:
                await self.log.game_cancelled(user_id, game)

                await self.map_(tracking)
                await self.transaction.commit()

                await self.game_views.game_view(game)
