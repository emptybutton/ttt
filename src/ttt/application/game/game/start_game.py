from asyncio import gather
from dataclasses import dataclass

from ttt.application.common.ports.emojis import Emojis
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.game.common.ports.game_views import GameViews
from ttt.application.game.common.ports.games import Games
from ttt.application.game.common.ports.waiting_locations import WaitingLocations
from ttt.application.player.common.ports.player_views import PlayerViews
from ttt.application.player.common.ports.players import Players
from ttt.entities.core.game.game import PlayersAlreadyInGameError, start_game
from ttt.entities.core.player.location import PlayerLocation
from ttt.entities.tools.tracking import Tracking


@dataclass(frozen=True, unsafe_hash=False)
class StartGame:
    map_: Map
    uuids: UUIDs
    emojis: Emojis
    players: Players
    player_views: PlayerViews
    games: Games
    game_views: GameViews
    waiting_locations: WaitingLocations
    transaction: Transaction

    async def __call__(self) -> None:
        async for player1_location, player2_location in self.waiting_locations:
            async with self.transaction, self.emojis:
                player1, player2 = await self.players.players_with_ids(
                    (player1_location.player_id, player2_location.player_id),
                )
                players_and_locations = tuple(zip(
                    (player1, player2),
                    (player1_location, player2_location),
                    strict=True,
                ))
                game_id, cell_id_matrix, player1_emoji, player2_emoji = (
                    await gather(
                        self.uuids.random_uuid(),
                        self.uuids.random_uuid_matrix((3, 3)),
                        self.emojis.random_emoji(),
                        self.emojis.random_emoji(),
                    )
                )

                if player1 is None:
                    await (
                        self.player_views.render_player_is_not_registered_view(
                            player1_location,
                        )
                    )
                if player2 is None:
                    await (
                        self.player_views.render_player_is_not_registered_view(
                            player2_location,
                        )
                    )
                if player1 is None or player2 is None:
                    await self.waiting_locations.push_many(tuple(
                        location
                        for player, location in players_and_locations
                        if player is not None
                    ))
                    continue

                tracking = Tracking()
                try:
                    game = start_game(
                        cell_id_matrix,
                        game_id,
                        player1,
                        player1_emoji,
                        player1_location.chat_id,
                        player2,
                        player2_emoji,
                        player2_location.chat_id,
                        tracking,
                    )

                except PlayersAlreadyInGameError as error:
                    locations_of_players_not_in_game = list[PlayerLocation]()
                    locations_of_players_in_game = list[PlayerLocation]()

                    for player, location in players_and_locations:
                        if player in error.players:
                            locations_of_players_in_game.append(location)
                        else:
                            locations_of_players_not_in_game.append(location)

                    await self.waiting_locations.push_many(
                        locations_of_players_not_in_game,
                    )
                    await self.game_views.render_player_already_in_game_views(
                        locations_of_players_in_game,
                    )
                    continue

                else:
                    await self.map_(tracking)

                    game_locations = (
                        player1_location.game(game.id),
                        player2_location.game(game.id),
                    )
                    await (
                        self.game_views
                        .render_started_game_view_with_locations(
                            game_locations, game,
                        )
                    )
