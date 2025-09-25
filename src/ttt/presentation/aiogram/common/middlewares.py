from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from dishka.integrations.aiogram import CONTAINER_NAME, AiogramMiddlewareData

from ttt.infrastructure.dishka.next_container import NextContainer


class AiogramNextContainerMiddleware(BaseMiddleware):
    def __init__(self, next_container: NextContainer) -> None:
        self.next_container = next_container

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:  # noqa: ANN401
        context = {
            TelegramObject: event,
            AiogramMiddlewareData: data,
        }
        async with self.next_container(context) as sub_container:
            data[CONTAINER_NAME] = sub_container
            return await handler(event, data)
