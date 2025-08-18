from ttt.presentation.aiogram.user.routes.handle_payment import (
    handle_payment_router,
)
from ttt.presentation.aiogram.user.routes.handle_pre_checkout_query import (
    handle_pre_checkout_query_router,
)
from ttt.presentation.aiogram.user.routes.start import (
    start_router,
)


user_routers = (
    start_router,
    handle_payment_router,
    handle_pre_checkout_query_router,
)
