from asyncio import gather
from collections.abc import Sequence
from dataclasses import dataclass

from aiogram import Bot
from aiogram_dialog import BgManagerFactory, ShowMode, StartMode
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.game.game.ports.game_views import GameViews
from ttt.entities.core.game.game import (
    Game,
)
from ttt.entities.core.user.location import UserGameLocation
from ttt.infrastructure.background_tasks import BackgroundTasks
from ttt.infrastructure.sqlalchemy.tables.game import TableGame
from ttt.infrastructure.sqlalchemy.tables.user import TableUser
from ttt.presentation.aiogram.common.dialogs import (
    ActiveGameView,
    CompletedGameView,
    DialogState,
)
from ttt.presentation.aiogram.game.messages import completed_game_sticker
from ttt.presentation.result_buffer import ResultBuffer


@dataclass(frozen=True, unsafe_hash=False)
class BackroundAiogramMessagesFromPostgresAsGameViews(GameViews):
    _session: AsyncSession
    _tasks: BackgroundTasks
    _bot: Bot
    _bg_dialog_manager_factory: BgManagerFactory
    _result_buffer: ResultBuffer

    async def waiting_for_game_view(self, user_id: int, /) -> None:
        dialog_manager = self._bg_dialog_manager_factory.bg(
            self._bot, user_id, user_id,
        )
        await dialog_manager.start(
            DialogState.game_mode_to_start_game,
            {"hint": "⚔️ Поиск игры начат"},
            StartMode.RESET_STACK,
        )

    async def current_game_view_with_user_id(self, user_id: int, /) -> None:
        join_condition = (
            (TableUser.id == user_id)
            & (TableUser.game_location_game_id == TableGame.id)
        )
        stmt = select(TableGame).join(TableUser, join_condition)
        table_game = await self._session.scalar(stmt)

        if table_game is None:
            return

        game = table_game.entity()
        self._result_buffer.result = ActiveGameView.of(game, user_id)

    async def game_view_with_locations(
        self,
        user_locations: Sequence[UserGameLocation],
        game: Game,
        /,
    ) -> None:
        match game.result:
            case None:
                await gather(*(
                    self._active_game_view(location, game)
                    for location in user_locations
                ))
            case _:
                await gather(*(
                    self._completed_game_view(location, game)
                    for location in user_locations
                ))

    async def started_game_view_with_locations(
        self,
        user_locations: Sequence[UserGameLocation],
        game: Game,
        /,
    ) -> None:
        for location in user_locations:
            dialog_manager = self._bg_dialog_manager_factory.bg(
                self._bot, location.user_id, location.user_id,
            )
            await dialog_manager.start(
                DialogState.game,
                ActiveGameView.of(game, location.user_id).window_data(),
                StartMode.RESET_STACK,
            )

    async def no_game_view(self, user_id: int, /) -> None:
        data = {"hint": "❌ Игра уже закончилась"}

        dialog_manager = self._bg_dialog_manager_factory.bg(
            self._bot, user_id, user_id,
        )
        await dialog_manager.start(
            DialogState.main, data, StartMode.RESET_STACK,
        )

    async def game_already_complteted_view(
        self,
        user_id: int,
        game: Game,
        /,
    ) -> None:
        dialog_manager = self._bg_dialog_manager_factory.bg(
            self._bot, user_id, user_id,
        )
        data = {"hint": "❌ Игра уже закончилась"}
        await dialog_manager.start(
            DialogState.game, data, StartMode.RESET_STACK,
        )

    async def not_current_user_view(
        self,
        user_id: int,
        game: Game,
        /,
    ) -> None:
        hint_data = {"hint": "❌ Сейчас не ваш ход"}
        game_data = ActiveGameView.of(game, user_id).window_data()
        data = hint_data | game_data

        dialog_manager = self._bg_dialog_manager_factory.bg(
            self._bot, user_id, user_id,
        )
        await dialog_manager.start(
            DialogState.game, data, StartMode.RESET_STACK,
        )

    async def no_cell_view(
        self,
        user_id: int,
        game: Game,
        /,
    ) -> None:
        raise NotImplementedError

    async def users_already_in_game_views(
        self,
        user_ids: Sequence[int],
        /,
    ) -> None: ...

    async def already_filled_cell_error(
        self,
        user_id: int,
        game: Game,
        /,
    ) -> None:
        hint_data = {"hint": "❌ Ячейка уже проставлена"}
        game_data = ActiveGameView.of(game, user_id).window_data()
        data = hint_data | game_data

        dialog_manager = self._bg_dialog_manager_factory.bg(
            self._bot, user_id, user_id,
        )
        await dialog_manager.start(
            DialogState.game, data, StartMode.RESET_STACK,
        )

    async def _active_game_view(
        self, location: UserGameLocation, game: Game,
    ) -> None:
        dialog_manager = self._bg_dialog_manager_factory.bg(
            self._bot, location.user_id, location.user_id,
        )

        view = ActiveGameView.of(game, location.user_id)
        data = view.window_data()

        await dialog_manager.start(
            DialogState.game, data, StartMode.RESET_STACK,
        )

    async def _completed_game_view(
        self,
        location: UserGameLocation,
        game: Game,
    ) -> None:
        dialog_manager = self._bg_dialog_manager_factory.bg(
            self._bot, location.user_id, location.user_id,
        )

        view = CompletedGameView.of(game, location.user_id)
        data = view.window_data()

        await gather(
            completed_game_sticker(
                self._bot, location.user_id, game, location.user_id,
            ),
            dialog_manager.start(
                DialogState.game,
                data,
                StartMode.RESET_STACK,
                ShowMode.DELETE_AND_SEND,
            ),
        )
