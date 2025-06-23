from collections.abc import Sequence
from dataclasses import dataclass

from aiogram import Bot
from aiogram.fsm.storage.base import BaseStorage

from ttt.application.game.ports.game_views import GameViews
from ttt.entities.core.game.game import Game, GameResult
from ttt.entities.core.player.location import PlayerGameLocation
from ttt.infrastructure.background_tasks import BackgroundTasks
from ttt.presentation.aiogram.game.messages import (
    completed_game_messages,
    maked_move_message,
    started_game_message,
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
                    player_locations, game,
                )
            case GameResult():
                self._completed_game_message_background_broadcast(
                    player_locations, game,
                )

    async def render_started_game_view_with_locations(
        self,
        player_locations: Sequence[PlayerGameLocation],
        game: Game,
        /,
    ) -> None:
        for location in player_locations:
            self._tasks.create_task(started_game_message(
                self._bot,
                location.chat_id,
                game,
                location.player_id,
            ))

    def _to_next_move_message_background_broadcast(
        self,
        player_locations: Sequence[PlayerGameLocation],
        game: Game,
    ) -> None:
        for location in player_locations:
            self._tasks.create_task(maked_move_message(
                self._bot,
                location.chat_id,
                game,
                location.player_id,
            ))

    def _completed_game_message_background_broadcast(
        self,
        player_locations: Sequence[PlayerGameLocation],
        game: Game,
    ) -> None:
        for location in player_locations:
            self._tasks.create_task(completed_game_messages(
                self._bot,
                location.chat_id,
                game,
                location.player_id,
            ))
