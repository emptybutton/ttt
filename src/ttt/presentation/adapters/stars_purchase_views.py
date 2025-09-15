from dataclasses import dataclass

from aiogram_dialog import ShowMode, StartMode

from ttt.application.stars_purchase.ports.stars_purchase_views import (
    StarsPurchaseViews,
)
from ttt.entities.core.stars_purchase.stars_purchase import StarsPurchase
from ttt.presentation.aiogram_dialog.common.dialog_manager_for_user import (
    DialogManagerForUser,
)
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState


@dataclass(frozen=True, unsafe_hash=False)
class AiogramStarsPurchaseViews(StarsPurchaseViews):
    _dialog_manager_for_user: DialogManagerForUser

    async def invalid_stars_for_stars_purchase_view(
        self,
        user_id: int,
        /,
    ) -> None:
        raise NotImplementedError

    async def stars_purchase_will_be_completed_view(
        self,
        user_id: int,
        /,
    ) -> None:
        manager = self._dialog_manager_for_user(user_id)
        await manager.start(
            MainDialogState.stars_shop,
            {"hint": "🌟 Звёзды скоро начислятся!"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )

    async def completed_stars_purchase_view(
        self,
        stars_purchase: StarsPurchase,
        /,
    ) -> None:
        manager = self._dialog_manager_for_user(stars_purchase.user.id)
        await manager.start(
            MainDialogState.stars_shop,
            {"hint": "🌟 Звезды начислились!"},
            StartMode.RESET_STACK,
            ShowMode.DELETE_AND_SEND,
        )
