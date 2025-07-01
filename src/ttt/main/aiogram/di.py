from dataclasses import dataclass
from typing import cast

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import (
    CallbackQuery,
    Message,
    TelegramObject,
)
from dishka import Provider, Scope, from_context, provide
from dishka.integrations.aiogram import AiogramMiddlewareData
from redis.asyncio import Redis

from ttt.application.common.ports.emojis import Emojis
from ttt.application.game.cancel_game import CancelGame
from ttt.application.game.make_move_in_game import MakeMoveInGame
from ttt.application.game.ports.game_views import GameViews
from ttt.application.game.start_game import StartGame
from ttt.application.game.wait_game import WaitGame
from ttt.application.player.buy_emoji import BuyEmoji
from ttt.application.player.complete_stars_purshase_payment import CompleteStarsPurshasePayment
from ttt.application.player.dto.common import PaidStarsPurchasePayment
from ttt.application.player.start_stars_purchase import (
    StartStarsPurchase,
)
from ttt.application.player.ports.player_fsm import PlayerFsm
from ttt.application.player.ports.player_views import PlayerViews
from ttt.application.player.ports.stars_purchase_payment_gateway import (
    StarsPurchasePaymentGateway,
)
from ttt.application.player.register_player import RegisterPlayer
from ttt.application.player.remove_emoji import RemoveEmoji
from ttt.application.player.select_emoji import SelectEmoji
from ttt.application.player.start_stars_purshase_payment_completion import (
    StartStarsPurshasePaymentCompletion,
)
from ttt.application.player.view_player import ViewPlayer
from ttt.application.player.wait_emoji_to_buy import WaitEmojiToBuy
from ttt.application.player.wait_emoji_to_select import WaitEmojiToSelect
from ttt.application.player.wait_stars_to_start_stars_purshase import (
    WaitStarsToStartStarsPurshase,
)
from ttt.infrastructure.buffer import Buffer
from ttt.infrastructure.pydantic_settings.secrets import Secrets
from ttt.presentation.adapters.emojis import PictographsAsEmojis
from ttt.presentation.adapters.game_views import (
    BackroundAiogramMessagesAsGameViews,
)
from ttt.presentation.adapters.player_fsm import AiogramTrustingPlayerFsm
from ttt.presentation.adapters.player_views import (
    AiogramMessagesFromPostgresAsPlayerViews,
)
from ttt.presentation.adapters.stars_purchase_payment_gateway import (
    AiogramInAndBufferOutStarsPurchasePaymentGateway,
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
    provide_paid_stars_purchase_payment_buffer = from_context(
        provides=Buffer[PaidStarsPurchasePayment],
        scope=Scope.APP,
    )

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

    @provide(scope=Scope.APP)
    def provide_stars_purchase_payment_gateway(
        self,
        secrets: Secrets,
        bot: Bot,
        buffer: Buffer[PaidStarsPurchasePayment],
    ) -> StarsPurchasePaymentGateway:
        return AiogramInAndBufferOutStarsPurchasePaymentGateway(
            buffer,
            bot,
            secrets.payments_token,
        )

    @provide(scope=Scope.REQUEST)
    async def unkillable_tasks(
        self,
        start_game: StartGame,
        start_stars_purshase_payment_completion: StartStarsPurshasePaymentCompletion,
        complete_stars_purshase_payment: CompleteStarsPurshasePayment,
    ) -> UnkillableTasks:
        tasks = UnkillableTasks()
        tasks.add(start_game)
        tasks.add(start_stars_purshase_payment_completion)
        tasks.add(complete_stars_purshase_payment)

        return tasks


class AiogramRequestDataProvider(Provider):
    provide_paid_stars_purchase_payment_buffer = from_context(
        provides=Buffer[PaidStarsPurchasePayment],
        scope=Scope.APP,
    )

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
        return cast(FSMContext, middleware_data["state"])

    provide_player_fsm = provide(
        AiogramTrustingPlayerFsm,
        provides=PlayerFsm,
        scope=Scope.REQUEST,
    )


class ApplicationWithAiogramRequestDataProvider(Provider):
    provide_buy_emoji = provide(BuyEmoji, scope=Scope.REQUEST)
    provide_wait_emoji_to_buy = provide(WaitEmojiToBuy, scope=Scope.REQUEST)
    provide_select_emoji = provide(SelectEmoji, scope=Scope.REQUEST)
    provide_wait_emoji_to_select = provide(
        WaitEmojiToSelect, scope=Scope.REQUEST,
    )
    probide_wait_stars_to_start_stars_purshase = provide(
        WaitStarsToStartStarsPurshase, scope=Scope.REQUEST,
    )
    probide_start_stars_purchase = provide(
        StartStarsPurchase, scope=Scope.REQUEST,
    )


class ApplicationWithoutAiogramRequestDataProvider(Provider):
    provide_view_player = provide(ViewPlayer, scope=Scope.REQUEST)
    provide_register_player = provide(RegisterPlayer, scope=Scope.REQUEST)
    provide_remove_emoji = provide(RemoveEmoji, scope=Scope.REQUEST)
    probide_complete_stars_purshase_payment = provide(
        CompleteStarsPurshasePayment, scope=Scope.REQUEST,
    )
    probide_start_stars_purshase_payment_completion = provide(
        StartStarsPurshasePaymentCompletion, scope=Scope.REQUEST,
    )

    provide_start_game = provide(StartGame, scope=Scope.REQUEST)
    provide_wait_game = provide(WaitGame, scope=Scope.REQUEST)
    provide_cancel_game = provide(CancelGame, scope=Scope.REQUEST)
    provide_make_move_in_game = provide(MakeMoveInGame, scope=Scope.REQUEST)
