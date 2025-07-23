from collections.abc import Sequence
from dataclasses import dataclass

from aiogram import Bot
from aiogram.fsm.storage.base import BaseStorage

from ttt.application.game.game.ports.game_views import GameViews
from ttt.entities.core.game.game import Game
from ttt.entities.core.user.location import UserGameLocation, UserLocation
from ttt.infrastructure.background_tasks import BackgroundTasks
from ttt.presentation.aiogram.game.messages import (
    already_completed_game_message,
    already_filled_cell_message,
    completed_game_messages,
    double_waiting_for_game_message,
    maked_move_message,
    message_to_start_game_with_ai,
    no_cell_message,
    no_game_message,
    not_current_user_message,
    started_game_message,
    user_already_in_game_message,
    waiting_for_game_message,
)


@dataclass(frozen=True, unsafe_hash=False)
class BackroundAiogramMessagesAsGameViews(GameViews):
    _tasks: BackgroundTasks
    _bot: Bot
    _storage: BaseStorage

    async def game_view_with_locations(
        self,
        user_locations: Sequence[UserGameLocation],
        game: Game,
        /,
    ) -> None:
        match game.result:
            case None:
                self._to_next_move_message_background_broadcast(
                    user_locations,
                    game,
                )
            case _:
                self._completed_game_message_background_broadcast(
                    user_locations,
                    game,
                )

    async def started_game_view_with_locations(
        self,
        user_locations: Sequence[UserGameLocation],
        game: Game,
        /,
    ) -> None:
        for location in user_locations:
            self._tasks.create_task(
                started_game_message(
                    self._bot,
                    location.chat_id,
                    game,
                    location.user_id,
                ),
            )

    async def no_game_view(
        self,
        user_location: UserLocation,
        /,
    ) -> None:
        self._tasks.create_task(
            no_game_message(self._bot, user_location.chat_id),
        )

    async def not_current_user_view(
        self,
        user_location: UserLocation,
        game: Game,
        /,
    ) -> None:
        self._tasks.create_task(
            not_current_user_message(self._bot, user_location.chat_id),
        )

    async def no_cell_view(
        self,
        user_location: UserLocation,
        game: Game,
        /,
    ) -> None:
        self._tasks.create_task(
            no_cell_message(self._bot, user_location.chat_id),
        )

    async def already_filled_cell_error(
        self,
        user_location: UserLocation,
        game: Game,
        /,
    ) -> None:
        self._tasks.create_task(
            already_filled_cell_message(self._bot, user_location.chat_id),
        )

    async def game_already_complteted_view(
        self,
        user_location: UserLocation,
        game: Game,
        /,
    ) -> None:
        self._tasks.create_task(
            already_completed_game_message(self._bot, user_location.chat_id),
        )

    async def user_already_in_game_views(
        self,
        locations: Sequence[UserLocation],
    ) -> None:
        for location in locations:
            self._tasks.create_task(
                user_already_in_game_message(self._bot, location.chat_id),
            )

    async def waiting_for_game_view(
        self,
        location: UserLocation,
    ) -> None:
        self._tasks.create_task(
            waiting_for_game_message(self._bot, location.chat_id),
        )

    async def waiting_for_ai_type_to_start_game_with_ai_view(
        self,
        location: UserLocation,
    ) -> None:
        self._tasks.create_task(
            message_to_start_game_with_ai(self._bot, location.chat_id),
        )

    async def double_waiting_for_game_view(
        self,
        location: UserLocation,
    ) -> None:
        self._tasks.create_task(
            double_waiting_for_game_message(self._bot, location.chat_id),
        )

    def _to_next_move_message_background_broadcast(
        self,
        user_locations: Sequence[UserGameLocation],
        game: Game,
    ) -> None:
        for location in user_locations:
            self._tasks.create_task(
                maked_move_message(
                    self._bot,
                    location.chat_id,
                    game,
                    location.user_id,
                ),
            )

    def _completed_game_message_background_broadcast(
        self,
        user_locations: Sequence[UserGameLocation],
        game: Game,
    ) -> None:
        for location in user_locations:
            self._tasks.create_task(
                completed_game_messages(
                    self._bot,
                    location.chat_id,
                    game,
                    location.user_id,
                ),
            )
