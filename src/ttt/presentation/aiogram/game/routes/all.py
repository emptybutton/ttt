from ttt.presentation.aiogram.game.routes.cancel_game import cancel_game_router
from ttt.presentation.aiogram.game.routes.game_with_ai.start_game_with_ai import (  # noqa: E501
    start_game_with_ai_router,
)
from ttt.presentation.aiogram.game.routes.game_with_ai.wait_ai_type_to_start_game_with_ai import (  # noqa: E501
    wait_ai_type_to_start_game_with_ai_router,
)
from ttt.presentation.aiogram.game.routes.make_move_in_game import (
    make_move_in_game_router,
)
from ttt.presentation.aiogram.game.routes.wait_game import wait_game_router


game_routers = (
    wait_game_router,
    cancel_game_router,
    make_move_in_game_router,
    wait_ai_type_to_start_game_with_ai_router,
    start_game_with_ai_router,
)
