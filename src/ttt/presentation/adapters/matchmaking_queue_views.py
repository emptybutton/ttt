from dataclasses import dataclass

from aiogram import Bot
from aiogram_dialog import BgManagerFactory, StartMode

from ttt.application.matchmaking_queue.common.matchmaking_queue_views import (
    CommonMatchmakingQueueViews,
)
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState


@dataclass(frozen=True, unsafe_hash=False)
class AiogramCommonMatchmakingQueueViews(CommonMatchmakingQueueViews):
    _bot: Bot
    _bg_dialog_manager_factory: BgManagerFactory

    async def waiting_for_game_view(self, user_id: int, /) -> None:
        dialog_manager = self._bg_dialog_manager_factory.bg(
            self._bot, user_id, user_id,
        )
        await dialog_manager.start(
            MainDialogState.game_mode_to_start_game,
            {"hint": "⚔️ Поиск игры начат"},
            StartMode.RESET_STACK,
        )

    async def double_waiting_for_game_view(self, user_id: int, /) -> None:
        dialog_manager = self._bg_dialog_manager_factory.bg(
            self._bot, user_id, user_id,
        )
        await dialog_manager.start(
            MainDialogState.game_mode_to_start_game,
            {"hint": "⚔️ Поиск игры начат"},
            StartMode.RESET_STACK,
        )
