from asyncio import gather
from dataclasses import dataclass

from ttt.application.common.ports.emojis import Emojis
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.game.game.ports.game_log import GameLog
from ttt.application.game.game.ports.game_starting_queue import (
    GameStartingQueue,
)
from ttt.application.game.game.ports.game_views import GameViews
from ttt.application.game.game.ports.games import Games
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.application.user.common.ports.users import Users
from ttt.entities.core.game.game import UsersAlreadyInGameError, start_game
from ttt.entities.tools.assertion import not_none
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class StartGame:
    map_: Map
    uuids: UUIDs
    emojis: Emojis
    users: Users
    user_views: CommonUserViews
    games: Games
    game_views: GameViews
    game_starting_queue: GameStartingQueue
    transaction: Transaction
    log: GameLog

    async def __call__(self) -> None:
        async for user1_id, user2_id in self.game_starting_queue:
            async with self.transaction, self.emojis:
                user1, user2 = await self.users.users_with_ids(
                    (user1_id, user2_id),
                )
                (
                    game_id,
                    cell_id_matrix,
                    user1_emoji,
                    user2_emoji,
                ) = await gather(
                    self.uuids.random_uuid(),
                    self.uuids.random_uuid_matrix((3, 3)),
                    self.emojis.random_emoji(),
                    self.emojis.random_emoji(),
                )

                if user1 is None:
                    await self.user_views.user_is_not_registered_view(user1_id)
                if user2 is None:
                    await self.user_views.user_is_not_registered_view(user2_id)
                if user1 is None or user2 is None:
                    await self.game_starting_queue.push_many(
                        tuple(
                            user.id
                            for user in (user1, user2)
                            if user is not None
                        ),
                    )
                    continue

                tracking = Tracking()
                try:
                    game = start_game(
                        cell_id_matrix,
                        game_id,
                        user1,
                        user1_emoji,
                        user2,
                        user2_emoji,
                        tracking,
                    )

                except UsersAlreadyInGameError as error:
                    ids_of_users_not_in_game = list[int]()
                    ids_of_users_in_game = list[int]()

                    for user in (user1, user2):
                        if user in error.users:
                            ids_of_users_in_game.append(user.id)
                        else:
                            ids_of_users_not_in_game.append(user.id)

                    await (
                        self.log
                        .users_already_in_game_to_start_game_via_game_starting_queue(
                            ids_of_users_in_game,
                        )
                    )
                    await (
                        self.log
                        .bad_attempt_to_start_game_via_game_starting_queue(
                            ids_of_users_not_in_game,
                        )
                    )

                    await self.game_starting_queue.push_many(
                        ids_of_users_not_in_game,
                    )
                    await self.game_views.users_already_in_game_views(
                        ids_of_users_in_game,
                    )
                    continue

                else:
                    await self.log.game_against_user_started(game)
                    await self.map_(tracking)

                    game_locations = (
                        not_none(user1.game_location),
                        not_none(user2.game_location),
                    )
                    await self.game_views.started_game_view_with_locations(
                        game_locations,
                        game,
                    )
