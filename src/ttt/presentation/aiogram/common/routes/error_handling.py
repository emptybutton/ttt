from typing import cast

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import ErrorEvent
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.api.exceptions import OutdatedIntent, UnknownIntent
from dishka.integrations.aiogram import FromDishka, inject
from structlog.types import FilteringBoundLogger

from ttt.infrastructure.structlog.logger import unexpected_error_log
from ttt.presentation.aiogram_dialog.main_dialog.common import MainDialogState


error_handling_router = Router(name=__name__)


@error_handling_router.error(
    ExceptionTypeFilter(UnknownIntent, OutdatedIntent),
)
async def _(_: ErrorEvent, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(
        MainDialogState.main,
        {"hint": "Сессия устарела"},
        StartMode.RESET_STACK,
    )


@error_handling_router.error(ExceptionTypeFilter(TelegramBadRequest))
@inject
async def _(
    event: ErrorEvent,
    logger: FromDishka[FilteringBoundLogger],
) -> None:
    error = cast(TelegramBadRequest, event.exception)

    if error.message not in {
        "Bad Request: chat not found",
        "Forbidden: bot was blocked by the user",
    }:
        await unexpected_error_log(logger, error)


@error_handling_router.error()
@inject
async def _(
    event: ErrorEvent,
    logger: FromDishka[FilteringBoundLogger],
) -> None:
    await unexpected_error_log(logger, event.exception)
