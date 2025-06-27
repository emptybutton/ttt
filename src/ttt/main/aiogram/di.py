from dataclasses import dataclass

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import (
    CallbackQuery,
    Message,
    TelegramObject,
)
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.aiogram import AiogramMiddlewareData
from dishka.integrations.aiogram import AiogramProvider as DishkaAiogramProvider
from redis.asyncio import Redis

from ttt.application.common.ports.emojis import Emojis
from ttt.application.game.ports.game_views import GameViews
from ttt.application.game.start_game import StartGame
from ttt.application.player.ports.player_fsm import PlayerFsm
from ttt.application.player.ports.player_views import PlayerViews
from ttt.infrastructure.pydantic_settings.secrets import Secrets
from ttt.main.common.di import CommonProvider
from ttt.presentation.adapters.emojis import PictographsAsEmojis
from ttt.presentation.adapters.game_views import (
    BackroundAiogramMessagesAsGameViews,
)
from ttt.presentation.adapters.player_fsm import AiogramTrustingPlayerFsm
from ttt.presentation.adapters.player_views import (
    AiogramMessagesFromPostgresAsPlayerViews,
)
from ttt.presentation.aiogram.common.bots import ttt_bot
from ttt.presentation.aiogram.common.routes.all import common_routers
from ttt.presentation.aiogram.game.routes.all import game_routers
from ttt.presentation.aiogram.player.routes.all import player_routers
from ttt.presentation.unkillable_tasks import UnkillableTasks


@dataclass(frozen=True, unsafe_hash=False)
class NoMessageInEventError(Exception):
    event: TelegramObject


class AiogramProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_strage(self, redis: Redis) -> BaseStorage:
        return RedisStorage(redis)

    @provide(scope=Scope.APP)
    def provide_dp(self, storage: BaseStorage) -> Dispatcher:
        dp = Dispatcher(name="main", storage=storage)
        dp.include_routers(
            *common_routers,
            *player_routers,
            *game_routers,
        )

        return dp

    @provide(scope=Scope.APP)
    async def provide_bot(self, secrets: Secrets) -> Bot:
        bot = Bot(secrets.bot_token)
        await ttt_bot(bot)

        return bot

    @provide(scope=Scope.REQUEST)
    def provide_message(self, event: TelegramObject) -> Message:
        match event:
            case Message():
                return event
            case CallbackQuery(message=Message() as message):
                return message
            case _:
                raise NoMessageInEventError(event)

    @provide(scope=Scope.REQUEST)
    def provide_fsm_context(
        self, middleware_data: AiogramMiddlewareData,
    ) -> FSMContext:
        return middleware_data["state"]

    provide_emoji = provide(
        PictographsAsEmojis,
        provides=Emojis,
        scope=Scope.REQUEST,
    )

    provide_game_views = provide(
        BackroundAiogramMessagesAsGameViews,
        provides=GameViews,
        scope=Scope.APP,
    )

    provide_player_views = provide(
        AiogramMessagesFromPostgresAsPlayerViews,
        provides=PlayerViews,
        scope=Scope.REQUEST,
    )
    provide_player_fsm = provide(
        AiogramTrustingPlayerFsm,
        provides=PlayerFsm,
        scope=Scope.REQUEST,
    )

    @provide(scope=Scope.REQUEST)
    async def unkillable_tasks(
        self, start_game: StartGame,
    ) -> UnkillableTasks:
        tasks = UnkillableTasks()
        tasks.add(start_game)

        return tasks


container = make_async_container(
    AiogramProvider(), DishkaAiogramProvider(), CommonProvider(),
)
