from ttt.presentation.aiogram.game.routes.make_move_in_game import (
    make_move_in_game_router,
)
from ttt.presentation.aiogram.game.routes.wait_game import wait_game_router


game_routers = (
    wait_game_router,
    make_move_in_game_router,
)
