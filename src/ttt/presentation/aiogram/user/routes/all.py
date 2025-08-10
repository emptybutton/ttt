from ttt.presentation.aiogram.user.routes.buy_emoji import buy_emoji_router
from ttt.presentation.aiogram.user.routes.handle_payment import (
    handle_payment_router,
)
from ttt.presentation.aiogram.user.routes.handle_pre_checkout_query import (
    handle_pre_checkout_query_router,
)
from ttt.presentation.aiogram.user.routes.select_emoji import (
    select_emoji_router,
)
from ttt.presentation.aiogram.user.routes.start import (
    start_router,
)
from ttt.presentation.aiogram.user.routes.start_stars_purchase import (
    start_stars_purchase_router,
)
from ttt.presentation.aiogram.user.routes.view_user import (
    view_user_router,
)


user_routers = (
    start_router,
    view_user_router,
    buy_emoji_router,
    select_emoji_router,
    start_stars_purchase_router,
    handle_payment_router,
    handle_pre_checkout_query_router,
)
