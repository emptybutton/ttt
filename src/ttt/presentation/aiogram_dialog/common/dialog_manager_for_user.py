from dataclasses import dataclass

from aiogram import Bot
from aiogram_dialog import BaseDialogManager, BgManagerFactory
from aiogram_dialog.manager.manager import ManagerImpl


@dataclass
class DialogManagerForUser:
    _event_dialog_manager: ManagerImpl | None
    _bg_manager_factory: BgManagerFactory
    _bot: Bot

    def __call__(self, user_id: int) -> BaseDialogManager:
        if self._event_dialog_manager is None:
            return self._bg(user_id)

        current_user = self._event_dialog_manager.event.from_user

        if current_user is None or current_user.id != user_id:
            return self._bg(user_id)

        return self._event_dialog_manager

    def _bg(self, user_id: int) -> BaseDialogManager:
        return self._bg_manager_factory.bg(self._bot, user_id, user_id)
