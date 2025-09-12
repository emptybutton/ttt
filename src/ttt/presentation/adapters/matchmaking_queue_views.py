from dataclasses import dataclass

from aiogram_dialog import StartMode

from ttt.application.matchmaking_queue.common.matchmaking_queue_views import (
    CommonMatchmakingQueueViews,
)
from ttt.presentation.aiogram_dialog.common.dialog_manager_for_user import (
    DialogManagerForUser,
)
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState


@dataclass(frozen=True, unsafe_hash=False)
class AiogramCommonMatchmakingQueueViews(CommonMatchmakingQueueViews):
    _dialog_manager_for_user: DialogManagerForUser

    async def waiting_for_game_view(self, user_id: int, /) -> None:
        dialog_manager = self._dialog_manager_for_user(user_id)

        await dialog_manager.start(
            MainDialogState.game_mode_to_start_game,
            {"hint": "⚔️ Поиск игры начат"},
            StartMode.RESET_STACK,
        )

    async def double_waiting_for_game_view(self, user_id: int, /) -> None:
        dialog_manager = self._dialog_manager_for_user(user_id)

        await dialog_manager.start(
            MainDialogState.game_mode_to_start_game,
            {"hint": "⚔️ Поиск игры начат"},
            StartMode.RESET_STACK,
        )
