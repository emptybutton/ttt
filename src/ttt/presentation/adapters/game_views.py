from collections.abc import Sequence
from dataclasses import dataclass

from aiogram import Bot
from aiogram.fsm.storage.base import BaseStorage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.game.game.ports.game_views import GameViews
from ttt.entities.core.game.game import Game
from ttt.entities.core.user.location import UserGameLocation
from ttt.infrastructure.background_tasks import BackgroundTasks
from ttt.infrastructure.sqlalchemy.tables.game import TableGame
from ttt.infrastructure.sqlalchemy.tables.user import TableUser
from ttt.presentation.aiogram.game.messages import (
    already_completed_game_message,
    already_filled_cell_message,
    completed_game_messages,
    double_waiting_for_game_message,
    game_message,
    game_modes_to_get_started_message,
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
class BackroundAiogramMessagesFromPostgresAsGameViews(GameViews):
    _session: AsyncSession
    _tasks: BackgroundTasks
    _bot: Bot
    _storage: BaseStorage

    async def current_game_view_with_user_id(self, user_id: int, /) -> None:
        join_condition = (
            (TableUser.id == user_id)
            & (TableUser.game_location_game_id == TableGame.id)
        )
        stmt = select(TableGame).join(TableUser, join_condition)
        table_game = await self._session.scalar(stmt)

        if table_game is None:
            self._tasks.create_task(no_game_message(self._bot, user_id))
        else:
            self._tasks.create_task(game_message(
                self._bot,
                user_id,
                table_game.entity(),
                user_id,
            ))

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
                    location.user_id,
                    game,
                    location.user_id,
                ),
            )

    async def no_game_view(
        self,
        user_id: int,
        /,
    ) -> None:
        self._tasks.create_task(
            no_game_message(self._bot, user_id),
        )

    async def not_current_user_view(
        self,
        user_id: int,
        game: Game,
        /,
    ) -> None:
        self._tasks.create_task(
            not_current_user_message(self._bot, user_id),
        )

    async def no_cell_view(
        self,
        user_id: int,
        game: Game,
        /,
    ) -> None:
        self._tasks.create_task(
            no_cell_message(self._bot, user_id),
        )

    async def already_filled_cell_error(
        self,
        user_id: int,
        game: Game,
        /,
    ) -> None:
        self._tasks.create_task(
            already_filled_cell_message(self._bot, user_id),
        )

    async def game_already_complteted_view(
        self,
        user_id: int,
        game: Game,
        /,
    ) -> None:
        self._tasks.create_task(
            already_completed_game_message(self._bot, user_id),
        )

    async def users_already_in_game_views(
        self,
        user_ids: Sequence[int],
    ) -> None:
        for user_id in user_ids:
            self._tasks.create_task(
                user_already_in_game_message(self._bot, user_id),
            )

    async def waiting_for_game_view(
        self,
        user_id: int,
    ) -> None:
        self._tasks.create_task(
            waiting_for_game_message(self._bot, user_id),
        )

    async def waiting_for_ai_type_to_start_game_with_ai_view(
        self,
        user_id: int,
    ) -> None:
        self._tasks.create_task(
            message_to_start_game_with_ai(self._bot, user_id),
        )

    async def double_waiting_for_game_view(
        self,
        user_id: int,
    ) -> None:
        self._tasks.create_task(
            double_waiting_for_game_message(self._bot, user_id),
        )

    async def game_modes_to_get_started_view(
        self,
        user_id: int,
        /,
    ) -> None:
        self._tasks.create_task(
            game_modes_to_get_started_message(self._bot, user_id),
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
                    location.user_id,
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
                    location.user_id,
                    game,
                    location.user_id,
                ),
            )
