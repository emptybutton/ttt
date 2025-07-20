from ttt.presentation.aiogram.common.routes.error_handling import (
    error_handling_router,
)
from ttt.presentation.aiogram.common.routes.help import help_router


common_routers = (
    help_router,
    error_handling_router,
)
