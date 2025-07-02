from collections.abc import Sequence
from dataclasses import dataclass

from aiogram import Bot
from aiogram.fsm.storage.base import BaseStorage

from ttt.application.game.common.ports.game_views import GameViews
from ttt.entities.core.game.game import Game
from ttt.entities.core.player.location import PlayerGameLocation, PlayerLocation
from ttt.infrastructure.background_tasks import BackgroundTasks
from ttt.presentation.aiogram.game.messages import (
    already_completed_game_message,
    already_filled_cell_message,
    completed_game_messages,
    double_waiting_for_game_message,
    maked_move_message,
    no_cell_message,
    no_game_message,
    not_current_player_message,
    player_already_in_game_message,
    started_game_message,
    waiting_for_game_message,
)


@dataclass(frozen=True, unsafe_hash=False)
class BackroundAiogramMessagesAsGameViews(GameViews):
    _tasks: BackgroundTasks
    _bot: Bot
    _storage: BaseStorage

    async def render_game_view_with_locations(
        self,
        player_locations: Sequence[PlayerGameLocation],
        game: Game,
        /,
    ) -> None:
        match game.result:
            case None:
                self._to_next_move_message_background_broadcast(
                    player_locations,
                    game,
                )
            case _:
                self._completed_game_message_background_broadcast(
                    player_locations,
                    game,
                )

    async def render_started_game_view_with_locations(
        self,
        player_locations: Sequence[PlayerGameLocation],
        game: Game,
        /,
    ) -> None:
        for location in player_locations:
            self._tasks.create_task(
                started_game_message(
                    self._bot,
                    location.chat_id,
                    game,
                    location.player_id,
                ),
            )

    async def render_no_game_view(
        self,
        player_location: PlayerLocation,
        /,
    ) -> None:
        self._tasks.create_task(
            no_game_message(self._bot, player_location.chat_id),
        )

    async def render_not_current_player_view(
        self,
        player_location: PlayerLocation,
        game: Game,
        /,
    ) -> None:
        self._tasks.create_task(
            not_current_player_message(self._bot, player_location.chat_id),
        )

    async def render_no_cell_view(
        self,
        player_location: PlayerLocation,
        game: Game,
        /,
    ) -> None:
        self._tasks.create_task(
            no_cell_message(self._bot, player_location.chat_id),
        )

    async def render_already_filled_cell_error(
        self,
        player_location: PlayerLocation,
        game: Game,
        /,
    ) -> None:
        self._tasks.create_task(
            already_filled_cell_message(self._bot, player_location.chat_id),
        )

    async def render_game_already_complteted_view(
        self,
        player_location: PlayerLocation,
        game: Game,
        /,
    ) -> None:
        self._tasks.create_task(
            already_completed_game_message(self._bot, player_location.chat_id),
        )

    async def render_player_already_in_game_views(
        self, locations: Sequence[PlayerLocation],
    ) -> None:
        for location in locations:
            self._tasks.create_task(
                player_already_in_game_message(self._bot, location.chat_id),
            )

    async def render_waiting_for_game_view(
        self, location: PlayerLocation,
    ) -> None:
        self._tasks.create_task(
            waiting_for_game_message(self._bot, location.chat_id),
        )

    async def render_double_waiting_for_game_view(
        self, location: PlayerLocation,
    ) -> None:
        self._tasks.create_task(
            double_waiting_for_game_message(self._bot, location.chat_id),
        )

    def _to_next_move_message_background_broadcast(
        self,
        player_locations: Sequence[PlayerGameLocation],
        game: Game,
    ) -> None:
        for location in player_locations:
            self._tasks.create_task(
                maked_move_message(
                    self._bot,
                    location.chat_id,
                    game,
                    location.player_id,
                ),
            )

    def _completed_game_message_background_broadcast(
        self,
        player_locations: Sequence[PlayerGameLocation],
        game: Game,
    ) -> None:
        for location in player_locations:
            self._tasks.create_task(
                completed_game_messages(
                    self._bot,
                    location.chat_id,
                    game,
                    location.player_id,
                ),
            )
