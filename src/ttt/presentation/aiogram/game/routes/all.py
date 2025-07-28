from ttt.presentation.aiogram.game.routes.game.back_to_game import (
    back_to_game_router,
)
from ttt.presentation.aiogram.game.routes.game.cancel_game import (
    cancel_game_router,
)
from ttt.presentation.aiogram.game.routes.game.make_move_in_game import (
    make_move_in_game_router,
)
from ttt.presentation.aiogram.game.routes.game.start_game_with_ai import (
    start_game_with_ai_router,
)
from ttt.presentation.aiogram.game.routes.game.view_game_modes_to_get_started import (  # noqa: E501
    view_game_modes_to_get_started_router,
)
from ttt.presentation.aiogram.game.routes.game.wait_ai_type_to_start_game_with_ai import (  # noqa: E501
    wait_ai_type_to_start_game_with_ai_router,
)
from ttt.presentation.aiogram.game.routes.game.wait_game import wait_game_router


game_routers = (
    view_game_modes_to_get_started_router,
    wait_game_router,
    cancel_game_router,
    make_move_in_game_router,
    wait_ai_type_to_start_game_with_ai_router,
    start_game_with_ai_router,
    back_to_game_router,
)
