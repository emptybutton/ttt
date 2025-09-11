from aiogram_dialog import Dialog

from ttt.presentation.aiogram_dialog.main_dialog.ai_type_to_start_game_window import (  # noqa: E501
    ai_type_to_start_game_window,
)
from ttt.presentation.aiogram_dialog.main_dialog.emoji_shop_window import (
    emoji_shop_window,
)
from ttt.presentation.aiogram_dialog.main_dialog.emojis_window import (
    emoji_window,
)
from ttt.presentation.aiogram_dialog.main_dialog.game_start_window import (
    game_start_window,
)
from ttt.presentation.aiogram_dialog.main_dialog.game_window import game_window
from ttt.presentation.aiogram_dialog.main_dialog.incoming_invitation_to_game_window import (  # noqa: E501
    incoming_invitation_to_game_window,
)
from ttt.presentation.aiogram_dialog.main_dialog.incoming_invitations_to_game_window import (  # noqa: E501
    incoming_invitations_to_game_window,
)
from ttt.presentation.aiogram_dialog.main_dialog.main_window import main_window
from ttt.presentation.aiogram_dialog.main_dialog.notification_window import (
    notification_window,
)
from ttt.presentation.aiogram_dialog.main_dialog.outcoming_invitations_to_game_window import (
    outcoming_invitations_to_game_window,
)
from ttt.presentation.aiogram_dialog.main_dialog.profile_window import (
    profile_window,
)
from ttt.presentation.aiogram_dialog.main_dialog.shop_window import shop_window
from ttt.presentation.aiogram_dialog.main_dialog.stars_shop_window import (
    stars_shop_window,
)


__all__ = ["main_dialog"]

main_dialog = Dialog(
    main_window,
    game_start_window,
    outcoming_invitations_to_game_window,
    ai_type_to_start_game_window,
    game_window,
    incoming_invitations_to_game_window,
    incoming_invitation_to_game_window,
    profile_window,
    emoji_window,
    shop_window,
    stars_shop_window,
    emoji_shop_window,
    notification_window,
)
