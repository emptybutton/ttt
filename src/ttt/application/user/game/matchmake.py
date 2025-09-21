from asyncio import gather
from contextlib import suppress
from dataclasses import dataclass

from ttt.application.common.ports.emojis import Emojis
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import (
    NotSerializableTransaction,
    SerializableTransaction,
)
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.user.common.ports.users import Users
from ttt.application.user.game.ports.user_log import GameUserLog
from ttt.application.user.game.ports.user_views import GameUserViews
from ttt.entities.core.game.game import Game
from ttt.entities.core.user.matchmaking import MatchmakingInput, matchmaking
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class Matchmake:
    map_: Map
    transaction: NotSerializableTransaction
    users: Users
    log: GameUserLog
    views: GameUserViews
    uuids: UUIDs
    emojis: Emojis

    async def __call__(self) -> None:
        async with self.transaction:
            tracking = Tracking()
            games = await self._result(tracking)

            await self.log.games_were_matched(games)
            await gather(
                self.views.matched_games_view(games),
                self._output_tracking(tracking),
            )

    async def _output_tracking(self, tracking: Tracking) -> None:
        await self.map_(tracking)
        await self.transaction.commit()

    async def _result(self, tracking: Tracking) -> list[Game]:
        users, input_ = await gather(
            self.users.some_users_waiting_for_matchmaking_to_matchmake(),
            self._matchmaking_input(),
        )
        max_rating, users_with_max_rating = (
            await self.users.max_rating_and_users_with_max_rating()
        )

        games = list[Game]()
        matchmaking_ = matchmaking(
            users, input_, max_rating, users_with_max_rating, tracking,
        )

        with suppress(StopIteration):
            games.append(next(matchmaking_))

            while True:
                games.append(matchmaking_.send(await self._matchmaking_input()))

        return games

    async def _matchmaking_input(self) -> MatchmakingInput:
        (
            cell_id_matrix,
            game_id,
            player1_random_emoji,
            player2_random_emoji,
        ) = await gather(
            self.uuids.random_uuid_matrix((3, 3)),
            self.uuids.random_uuid(),
            self.emojis.random_emoji(),
            self.emojis.random_emoji(),
        )
        return MatchmakingInput(
            cell_id_matrix,
            game_id,
            player1_random_emoji,
            player2_random_emoji,
        )
