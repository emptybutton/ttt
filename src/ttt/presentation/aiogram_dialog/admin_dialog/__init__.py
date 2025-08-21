from aiogram_dialog import Dialog

from ttt.presentation.aiogram_dialog.admin_dialog.main_window import main_window


__all__ = ["admin_dialog"]

admin_dialog = Dialog(main_window)
