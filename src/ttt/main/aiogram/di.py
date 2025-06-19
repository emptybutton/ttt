from dataclasses import dataclass

from aiogram import Bot, Dispatcher
from aiogram.types import (
    CallbackQuery,
    Message,
    TelegramObject,
)
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.aiogram import AiogramProvider as DishkaAiogramProvider

from ttt.infrastructure.pydantic_settings.secrets import Secrets
from ttt.main.common.di import CommonProvider
from ttt.presentation.aiogram.routes.all import all_routers


@dataclass(frozen=True, unsafe_hash=False)
class NoMessageInEventError(Exception):
    event: TelegramObject


class AiogramProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_dp(self) -> Dispatcher:
        dp = Dispatcher(name="main")
        dp.include_routers(*all_routers)

        return dp

    @provide(scope=Scope.APP)
    def provide_bot(self, secrets: Secrets) -> Bot:
        return Bot(secrets.bot_token)

    @provide(scope=Scope.REQUEST)
    def provide_message(self, event: TelegramObject) -> Message:
        match event:
            case Message():
                return event
            case CallbackQuery(message=Message() as message):
                return message
            case _:
                raise NoMessageInEventError(event)


container = make_async_container(
    AiogramProvider(), DishkaAiogramProvider(), CommonProvider(),
)
