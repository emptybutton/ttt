from dataclasses import dataclass

from ttt.application.common.ports.emojis import Emojis
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.randoms import Randoms
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.game.common.ports.game_views import GameViews
from ttt.application.game.common.ports.games import Games
from ttt.application.game.common.ports.waiting_locations import WaitingLocations
from ttt.application.user.common.ports.user_views import UserViews
from ttt.application.user.common.ports.users import Users
from ttt.entities.core.game.ai import AiType
from ttt.entities.core.game.game import start_game_with_ai
from ttt.entities.core.user.location import UserLocation
from ttt.entities.core.user.user import UserAlreadyInGameError
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class StartGameWithAi:
    map_: Map
    uuids: UUIDs
    emojis: Emojis
    randoms: Randoms
    users: Users
    user_views: UserViews
    games: Games
    game_views: GameViews
    waiting_locations: WaitingLocations
    transaction: Transaction

    async def __call__(self, location: UserLocation, ai_type: AiType) -> None:
        game_id = await self.uuids.random_uuid()
        ai_id = await self.uuids.random_uuid()
        cell_id_matrix = await self.uuids.random_uuid_matrix((3, 3))
        user_emoji = await self.emojis.random_emoji()
        ai_emoji = await self.emojis.random_emoji()
        player_order_random = await self.randoms.random()

        async with self.transaction:
            user = await self.users.user_with_id(location.user_id)

            if user is None:
                await self.user_views.render_user_is_not_registered_view(
                    location,
                )
                return

            try:
                tracking = Tracking()
                game = start_game_with_ai(
                    cell_id_matrix,
                    game_id,
                    user,
                    user_emoji,
                    location.chat_id,
                    ai_id,
                    ai_type,
                    ai_emoji,
                    player_order_random,
                    tracking,
                )
            except UserAlreadyInGameError:
                await self.game_views.render_user_already_in_game_views(
                    [location],
                )
            else:
                await self.map_(tracking)
                await (
                    self.game_views
                    .render_started_game_view_with_locations(
                        [location.game(game.id)], game,
                    )
                )
