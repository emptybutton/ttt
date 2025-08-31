from aiogram_dialog import Dialog

from ttt.presentation.aiogram_dialog.admin_dialog.main_window import main_window
from ttt.presentation.aiogram_dialog.admin_dialog.other_user_profile_window import (  # noqa: E501
    other_user_profile_window,
)


__all__ = ["admin_dialog"]

admin_dialog = Dialog(
    main_window,
    other_user_profile_window,
)
