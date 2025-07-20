from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.state import any_state
from aiogram.types import ErrorEvent, Message
from dishka.integrations.aiogram import FromDishka, inject
from structlog.types import FilteringBoundLogger

from ttt.entities.tools.assertion import not_none
from ttt.infrastructure.structlog.logger import unexpected_error_log
from ttt.presentation.aiogram.common.messages import help_message


error_handling_router = Router(name=__name__)


@error_handling_router.error()
@inject
async def _(
    event: ErrorEvent, logger: FromDishka[FilteringBoundLogger],
) -> None:
    await unexpected_error_log(logger, event.exception)
