from ttt.presentation.aiogram.user.routes.emoji_purchase.buy_emoji import (
    buy_emoji_router,
)
from ttt.presentation.aiogram.user.routes.emoji_purchase.wait_emoji_to_buy import (  # noqa: E501
    wait_emoji_to_buy_router,
)
from ttt.presentation.aiogram.user.routes.emoji_selection.select_emoji import (
    select_emoji_router,
)
from ttt.presentation.aiogram.user.routes.emoji_selection.wait_emoji_to_select import (  # noqa: E501
    wait_emoji_to_buy_select_router,
)
from ttt.presentation.aiogram.user.routes.handle_payment import (
    handle_payment_router,
)
from ttt.presentation.aiogram.user.routes.handle_pre_checkout_query import (
    handle_pre_checkout_query_router,
)
from ttt.presentation.aiogram.user.routes.register_user import (
    register_user_router,
)
from ttt.presentation.aiogram.user.routes.remove_emoji import (
    remove_emoji_router,
)
from ttt.presentation.aiogram.user.routes.stars_purchase.start_stars_purchase import (  # noqa: E501
    start_stars_purchase_router,
)
from ttt.presentation.aiogram.user.routes.stars_purchase.wait_stars_to_start_stars_purchase import (  # noqa: E501
    wait_stars_to_start_stars_purchase_router,
)
from ttt.presentation.aiogram.user.routes.view_user import (
    view_user_router,
)


user_routers = (
    register_user_router,
    view_user_router,
    buy_emoji_router,
    wait_emoji_to_buy_router,
    select_emoji_router,
    wait_emoji_to_buy_select_router,
    remove_emoji_router,
    start_stars_purchase_router,
    handle_payment_router,
    handle_pre_checkout_query_router,
    wait_stars_to_start_stars_purchase_router,
)
