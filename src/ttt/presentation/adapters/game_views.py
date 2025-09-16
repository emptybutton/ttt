from asyncio import gather
from dataclasses import dataclass

from aiogram import Bot
from aiogram_dialog import ShowMode, StartMode
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ttt.application.game.game.ports.game_views import GameViews
from ttt.entities.core.game.game import (
    Game,
)
from ttt.infrastructure.sqlalchemy.tables.game import TableGame
from ttt.infrastructure.sqlalchemy.tables.user import TableUser
from ttt.presentation.aiogram.game.messages import completed_game_sticker
from ttt.presentation.aiogram_dialog.common.dialog_manager_for_user import (
    DialogManagerForUser,
)
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState
from ttt.presentation.aiogram_dialog.main_dialog.game_window import (
    ActiveGameView,
    CompletedGameView,
)
from ttt.presentation.result_buffer import ResultBuffer


@dataclass(frozen=True, unsafe_hash=False)
class AiogramGameViews(GameViews):
    _session: AsyncSession
    _bot: Bot
    _dialog_manager_for_user: DialogManagerForUser
    _result_buffer: ResultBuffer

    async def current_game_view_with_user_id(self, user_id: int, /) -> None:
        join_condition = (
            (TableUser.id == user_id)
            & (TableUser.current_game_id == TableGame.id)
        )
        stmt = select(TableGame).join(TableUser, join_condition)
        table_game = await self._session.scalar(stmt)

        if table_game is None:
            return

        game = table_game.entity()
        self._result_buffer.result = ActiveGameView.of(game, user_id)

    async def game_view(self, game: Game, /) -> None:
        match game.result:
            case None:
                await gather(*(
                    self._active_game_view(user.id, game)
                    for user in game.users()
                ))
            case _:
                await gather(*(
                    self._completed_game_view(user.id, game)
                    for user in game.users()
                ))

    async def started_game_view(self, game: Game, /) -> None:
        await gather(*(
            self._started_game_view(user.id, game)
            for user in game.users()
        ))

    async def no_game_view(self, user_id: int, /) -> None:
        dialog_manager = self._dialog_manager_for_user(user_id)

        data = {"hint": "❌ Игра уже закончилась"}
        await dialog_manager.start(
            MainDialogState.main, data, StartMode.RESET_STACK,
        )

    async def game_already_complteted_view(
        self,
        user_id: int,
        game: Game,
        /,
    ) -> None:
        dialog_manager = self._dialog_manager_for_user(user_id)

        data = {"hint": "❌ Игра уже закончилась"}
        await dialog_manager.start(
            MainDialogState.game, data, StartMode.RESET_STACK,
        )

    async def not_current_user_view(
        self,
        user_id: int,
        game: Game,
        /,
    ) -> None:
        dialog_manager = self._dialog_manager_for_user(user_id)

        hint_data = {"hint": "❌ Сейчас не ваш ход"}
        game_data = ActiveGameView.of(game, user_id).window_data()
        data = hint_data | game_data

        await dialog_manager.start(
            MainDialogState.game, data, StartMode.RESET_STACK,
        )

    async def no_cell_view(
        self,
        user_id: int,
        game: Game,
        /,
    ) -> None:
        raise NotImplementedError

    async def user_already_in_game_view(self, user_id: int, /) -> None:
        dialog_manager = self._dialog_manager_for_user(user_id)

        data = {"hint": "❌ Вы уже в игре"}
        await dialog_manager.start(
            MainDialogState.main, data, StartMode.RESET_STACK,
        )

    async def already_filled_cell_error(
        self,
        user_id: int,
        game: Game,
        /,
    ) -> None:
        dialog_manager = self._dialog_manager_for_user(user_id)

        hint_data = {"hint": "❌ Ячейка уже проставлена"}
        game_data = ActiveGameView.of(game, user_id).window_data()
        data = hint_data | game_data

        await dialog_manager.start(
            MainDialogState.game, data, StartMode.RESET_STACK,
        )

    async def _started_game_view(self, user_id: int, game: Game, /) -> None:
        dialog_manager = self._dialog_manager_for_user(user_id)
        await dialog_manager.start(
            MainDialogState.game,
            ActiveGameView.of(game, user_id).window_data(),
            StartMode.RESET_STACK,
        )

    async def _active_game_view(self, user_id: int, game: Game) -> None:
        dialog_manager = self._dialog_manager_for_user(user_id)

        view = ActiveGameView.of(game, user_id)
        data = view.window_data()

        await dialog_manager.start(
            MainDialogState.game, data, StartMode.RESET_STACK,
        )

    async def _completed_game_view(self, user_id: int, game: Game) -> None:
        dialog_manager = self._dialog_manager_for_user(user_id)

        view = CompletedGameView.of(game, user_id)
        data = view.window_data()

        await completed_game_sticker(self._bot, user_id, game, user_id)
        await dialog_manager.start(
            MainDialogState.game,
            data,
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )
