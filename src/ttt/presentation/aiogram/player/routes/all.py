from ttt.presentation.aiogram.player.routes.emoji_purchase.buy_emoji import (
    buy_emoji_router,
)
from ttt.presentation.aiogram.player.routes.emoji_purchase.wait_emoji_to_buy import (  # noqa: E501
    wait_emoji_to_buy_router,
)
from ttt.presentation.aiogram.player.routes.emoji_selection.select_emoji import (  # noqa: E501
    select_emoji_router,
)
from ttt.presentation.aiogram.player.routes.emoji_selection.wait_emoji_to_select import (  # noqa: E501
    wait_emoji_to_buy_select_router,
)
from ttt.presentation.aiogram.player.routes.handle_payment import (
    handle_payment_router,
)
from ttt.presentation.aiogram.player.routes.handle_pre_checkout_query import (
    handle_pre_checkout_query_router,
)
from ttt.presentation.aiogram.player.routes.register_player import (
    register_player_router,
)
from ttt.presentation.aiogram.player.routes.remove_emoji import (
    remove_emoji_router,
)
from ttt.presentation.aiogram.player.routes.stars_purchase.start_stars_purchase import (  # noqa: E501
    start_stars_purchase_router,
)
from ttt.presentation.aiogram.player.routes.stars_purchase.wait_stars_to_start_stars_purshase import (  # noqa: E501
    wait_stars_to_start_stars_purshase_router,
)
from ttt.presentation.aiogram.player.routes.view_player import (
    view_player_router,
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
