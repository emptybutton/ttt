from asyncio import gather
from dataclasses import dataclass

from ttt.application.common.ports.emojis import Emojis
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.game.common.ports.game_views import GameViews
from ttt.application.game.common.ports.games import Games
from ttt.application.game.common.ports.waiting_locations import WaitingLocations
from ttt.application.user.common.ports.user_views import UserViews
from ttt.application.user.common.ports.users import Users
from ttt.entities.core.game.game import UsersAlreadyInGameError, start_game
from ttt.entities.core.user.location import UserLocation
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class StartGame:
    map_: Map
    uuids: UUIDs
    emojis: Emojis
    users: Users
    user_views: UserViews
    games: Games
    game_views: GameViews
    waiting_locations: WaitingLocations
    transaction: Transaction

    async def __call__(self) -> None:
        async for user1_location, user2_location in self.waiting_locations:
            async with self.transaction, self.emojis:
                user1, user2 = await self.users.users_with_ids(
                    (user1_location.user_id, user2_location.user_id),
                )
                users_and_locations = tuple(zip(
                    (user1, user2),
                    (user1_location, user2_location),
                    strict=True,
                ))
                game_id, cell_id_matrix, user1_emoji, user2_emoji = (
                    await gather(
                        self.uuids.random_uuid(),
                        self.uuids.random_uuid_matrix((3, 3)),
                        self.emojis.random_emoji(),
                        self.emojis.random_emoji(),
                    )
                )

                if user1 is None:
                    await (
                        self.user_views.render_user_is_not_registered_view(
                            user1_location,
                        )
                    )
                if user2 is None:
                    await (
                        self.user_views.render_user_is_not_registered_view(
                            user2_location,
                        )
                    )
                if user1 is None or user2 is None:
                    await self.waiting_locations.push_many(tuple(
                        location
                        for user, location in users_and_locations
                        if user is not None
                    ))
                    continue

                tracking = Tracking()
                try:
                    game = start_game(
                        cell_id_matrix,
                        game_id,
                        user1,
                        user1_emoji,
                        user1_location.chat_id,
                        user2,
                        user2_emoji,
                        user2_location.chat_id,
                        tracking,
                    )

                except UsersAlreadyInGameError as error:
                    locations_of_users_not_in_game = list[UserLocation]()
                    locations_of_users_in_game = list[UserLocation]()

                    for user, location in users_and_locations:
                        if user in error.users:
                            locations_of_users_in_game.append(location)
                        else:
                            locations_of_users_not_in_game.append(location)

                    await self.waiting_locations.push_many(
                        locations_of_users_not_in_game,
                    )
                    await self.game_views.render_user_already_in_game_views(
                        locations_of_users_in_game,
                    )
                    continue

                else:
                    await self.map_(tracking)

                    game_locations = (
                        user1_location.game(game.id),
                        user2_location.game(game.id),
                    )
                    await (
                        self.game_views
                        .render_started_game_view_with_locations(
                            game_locations, game,
                        )
                    )
