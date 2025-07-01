from ttt.presentation.aiogram.player.routes.buy_emoji import buy_emoji_router
from ttt.presentation.aiogram.player.routes.handle_payment import (
    handle_payment_router,
)
from ttt.presentation.aiogram.player.routes.handle_pre_checkout_query import (
    handle_pre_checkout_query_router,
)
from ttt.presentation.aiogram.player.routes.start_stars_purchase import (  # noqa: E501
    start_stars_purchase_router,
)
from ttt.presentation.aiogram.player.routes.register_player import (
    register_player_router,
)
from ttt.presentation.aiogram.player.routes.remove_emoji import (
    remove_emoji_router,
)
from ttt.presentation.aiogram.player.routes.select_emoji import (
    select_emoji_router,
)
from ttt.presentation.aiogram.player.routes.view_player import (
    view_player_router,
)
from ttt.presentation.aiogram.player.routes.wait_emoji_to_buy import (
    wait_emoji_to_buy_router,
)
from ttt.presentation.aiogram.player.routes.wait_emoji_to_select import (
    wait_emoji_to_buy_select_router,
)
from ttt.presentation.aiogram.player.routes.wait_stars_to_start_stars_purshase import (  # noqa: E501
    wait_stars_to_start_stars_purshase_router,
)


player_routers = (
    register_player_router,
    view_player_router,
    buy_emoji_router,
    wait_emoji_to_buy_router,
    select_emoji_router,
    wait_emoji_to_buy_select_router,
    remove_emoji_router,
    start_stars_purchase_router,
    handle_payment_router,
    handle_pre_checkout_query_router,
    wait_stars_to_start_stars_purshase_router,
)
