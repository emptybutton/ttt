from ttt.presentation.aiogram.routes.other.all import other_routers
from ttt.presentation.aiogram.routes.player.all import player_routers


all_routers = (
    *player_routers,
    *other_routers,
)
