from aiogram import Router
from aiogram.types import ErrorEvent
from dishka.integrations.aiogram import FromDishka, inject
from structlog.types import FilteringBoundLogger

from ttt.infrastructure.structlog.logger import unexpected_error_log


error_handling_router = Router(name=__name__)


@error_handling_router.error()
@inject
async def _(
    event: ErrorEvent, logger: FromDishka[FilteringBoundLogger],
) -> None:
    await unexpected_error_log(logger, event.exception)
