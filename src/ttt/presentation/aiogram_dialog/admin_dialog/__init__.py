from aiogram_dialog import Dialog

from ttt.presentation.aiogram_dialog.admin_dialog.authorize_other_user_as_admin_window import (  # noqa: E501
    authorize_other_user_as_admin_window,
)
from ttt.presentation.aiogram_dialog.admin_dialog.change_other_user_account1_window import (  # noqa: E501
    change_other_user_account1_window,
)
from ttt.presentation.aiogram_dialog.admin_dialog.change_other_user_account2_window import (  # noqa: E501
    change_other_user_account2_window,
)
from ttt.presentation.aiogram_dialog.admin_dialog.deauthorize_other_user_as_admin_window import (  # noqa: E501
    deauthorize_other_user_as_admin_window,
)
from ttt.presentation.aiogram_dialog.admin_dialog.main_window import main_window
from ttt.presentation.aiogram_dialog.admin_dialog.other_user_profile_window import (  # noqa: E501
    other_user_profile_window,
)
from ttt.presentation.aiogram_dialog.admin_dialog.relinquish_admin_right1_window import (  # noqa: E501
    relinquish_admin_right1_window,
)
from ttt.presentation.aiogram_dialog.admin_dialog.relinquish_admin_right2_window import (  # noqa: E501
    relinquish_admin_right2_window,
)


__all__ = ["admin_dialog"]

admin_dialog = Dialog(
    main_window,
    other_user_profile_window,
    authorize_other_user_as_admin_window,
    deauthorize_other_user_as_admin_window,
    relinquish_admin_right1_window,
    relinquish_admin_right2_window,
    change_other_user_account1_window,
    change_other_user_account2_window,
)
