from collections.abc import Sequence
from dataclasses import dataclass

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import BaseStorage, StorageKey

from ttt.application.game.ports.game_views import GameViews
from ttt.entities.core.game.game import Game, GameResult
from ttt.entities.core.player.location import PlayerGameLocation
from ttt.infrastructure.background_tasks import BackgroundTasks
from ttt.presentation.aiogram.game.messages import (
    completed_game_message,
    maked_move_message,
    started_game_message,
)
from ttt.presentation.aiogram.game.routes.game import GameViewState


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
            self._tasks.create_task(
                self._render_started_game_view_with_location(location, game),
            )

    async def _render_started_game_view_with_location(
        self, location: PlayerGameLocation, game: Game, /,
    ) -> None:
        storage_key = StorageKey(
            bot_id=self._bot.id,
            user_id=location.player_id,
            chat_id=location.chat_id,
        )
        state = FSMContext(storage=self._storage, key=storage_key)
        await state.set_state(GameViewState.waiting_move)

        await started_game_message(
            self._bot,
            location.chat_id,
            game,
            location.player_id,
        )

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
            self._tasks.create_task(completed_game_message(
                self._bot,
                location.chat_id,
                game,
                location.player_id,
            ))
