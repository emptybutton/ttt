from dataclasses import dataclass
from typing import cast

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import (
    CallbackQuery,
    Message,
    PreCheckoutQuery,
    TelegramObject,
)
from dishka import (
    Provider,
    Scope,
    from_context,
    provide,
)
from dishka.integrations.aiogram import AiogramMiddlewareData
from redis.asyncio import Redis
from structlog.types import FilteringBoundLogger

from ttt.application.common.ports.emojis import Emojis
from ttt.application.game.game.cancel_game import CancelGame
from ttt.application.game.game.make_move_in_game import MakeMoveInGame
from ttt.application.game.game.ports.game_views import GameViews
from ttt.application.game.game.start_game import StartGame
from ttt.application.game.game.start_game_with_ai import StartGameWithAi
from ttt.application.game.game.wait_ai_type_to_start_game_with_ai import (
    WaitAiTypeToStartGameWithAi,
)
from ttt.application.game.game.wait_game import WaitGame
from ttt.application.user.common.dto.common import PaidStarsPurchasePayment
from ttt.application.user.common.ports.stars_purchase_payment_gateway import (
    StarsPurchasePaymentGateway,
)
from ttt.application.user.common.ports.user_fsm import UserFsm
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.application.user.emoji_purchase.buy_emoji import BuyEmoji
from ttt.application.user.emoji_purchase.ports.user_views import (
    EmojiPurchaseUserViews,
)
from ttt.application.user.emoji_purchase.wait_emoji_to_buy import (
    WaitEmojiToBuy,
)
from ttt.application.user.emoji_selection.ports.user_views import (
    EmojiSelectionUserViews,
)
from ttt.application.user.emoji_selection.select_emoji import SelectEmoji
from ttt.application.user.emoji_selection.wait_emoji_to_select import (
    WaitEmojiToSelect,
)
from ttt.application.user.register_user import RegisterUser
from ttt.application.user.remove_emoji import RemoveEmoji
from ttt.application.user.stars_purchase.complete_stars_purshase_payment import (  # noqa: E501
    CompleteStarsPurshasePayment,
)
from ttt.application.user.stars_purchase.ports.user_views import (
    StarsPurchaseUserViews,
)
from ttt.application.user.stars_purchase.start_stars_purchase import (
    StartStarsPurchase,
)
from ttt.application.user.stars_purchase.start_stars_purchase_payment import (
    StartStarsPurchasePayment,
)
from ttt.application.user.stars_purchase.start_stars_purshase_payment_completion import (  # noqa: E501
    StartStarsPurshasePaymentCompletion,
)
from ttt.application.user.stars_purchase.wait_stars_to_start_stars_purshase import (  # noqa: E501
    WaitStarsToStartStarsPurshase,
)
from ttt.application.user.view_user import ViewUser
from ttt.infrastructure.buffer import Buffer
from ttt.infrastructure.pydantic_settings.secrets import Secrets
from ttt.presentation.adapters.emojis import PictographsAsEmojis
from ttt.presentation.adapters.game_views import (
    BackroundAiogramMessagesAsGameViews,
)
from ttt.presentation.adapters.stars_purchase_payment_gateway import (
    AiogramInAndBufferOutStarsPurchasePaymentGateway,
)
from ttt.presentation.adapters.user_fsm import AiogramTrustingUserFsm
from ttt.presentation.adapters.user_views import (
    AiogramMessagesAsEmojiPurchaseUserViews,
    AiogramMessagesAsEmojiSelectionUserViews,
    AiogramMessagesAsStarsPurchaseUserViews,
    AiogramMessagesFromPostgresAsCommonUserViews,
)
from ttt.presentation.aiogram.common.bots import ttt_bot
from ttt.presentation.aiogram.common.routes.all import common_routers
from ttt.presentation.aiogram.game.routes.all import game_routers
from ttt.presentation.aiogram.user.routes.all import user_routers
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
            *user_routers,
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

    provide_user_views = provide(
        AiogramMessagesFromPostgresAsCommonUserViews,
        provides=CommonUserViews,
        scope=Scope.REQUEST,
    )
    provide_stars_purchase_user_views = provide(
        AiogramMessagesAsStarsPurchaseUserViews,
        provides=StarsPurchaseUserViews,
        scope=Scope.APP,
    )
    provide_emoji_selection_user_views = provide(
        AiogramMessagesAsEmojiSelectionUserViews,
        provides=EmojiSelectionUserViews,
        scope=Scope.APP,
    )
    provide_emoji_purchase_user_views = provide(
        AiogramMessagesAsEmojiPurchaseUserViews,
        provides=EmojiPurchaseUserViews,
        scope=Scope.APP,
    )

    @provide(scope=Scope.APP)
    def provide_stars_purchase_payment_gateway(
        self,
        secrets: Secrets,
        bot: Bot,
        buffer: Buffer[PaidStarsPurchasePayment],
    ) -> StarsPurchasePaymentGateway:
        return AiogramInAndBufferOutStarsPurchasePaymentGateway(
            None,
            buffer,
            bot,
            secrets.payments_token,
        )

    @provide(scope=Scope.REQUEST)
    async def unkillable_tasks(
        self,
        logger: FilteringBoundLogger,
        start_game: StartGame,
        start_stars_purshase_payment_completion: (
            StartStarsPurshasePaymentCompletion
        ),
        complete_stars_purshase_payment: CompleteStarsPurshasePayment,
    ) -> UnkillableTasks:
        tasks = UnkillableTasks(logger)
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
    def provide_pre_checkout_query(
        self,
        event: TelegramObject,
    ) -> PreCheckoutQuery | None:
        match event:
            case PreCheckoutQuery():
                return event
            case _:
                return None

    @provide(scope=Scope.REQUEST)
    def provide_fsm_context(
        self,
        middleware_data: AiogramMiddlewareData,
    ) -> FSMContext:
        return cast(FSMContext, middleware_data["state"])

    provide_user_fsm = provide(
        AiogramTrustingUserFsm,
        provides=UserFsm,
        scope=Scope.REQUEST,
    )

    @provide(scope=Scope.REQUEST)
    def provide_stars_purchase_payment_gateway(
        self,
        pre_checkout_query: PreCheckoutQuery | None,
        secrets: Secrets,
        bot: Bot,
        buffer: Buffer[PaidStarsPurchasePayment],
    ) -> StarsPurchasePaymentGateway:
        return AiogramInAndBufferOutStarsPurchasePaymentGateway(
            pre_checkout_query,
            buffer,
            bot,
            secrets.payments_token,
        )


class ApplicationWithAiogramRequestDataProvider(Provider):
    provide_buy_emoji = provide(BuyEmoji, scope=Scope.REQUEST)
    provide_wait_emoji_to_buy = provide(WaitEmojiToBuy, scope=Scope.REQUEST)
    provide_select_emoji = provide(SelectEmoji, scope=Scope.REQUEST)
    provide_wait_emoji_to_select = provide(
        WaitEmojiToSelect,
        scope=Scope.REQUEST,
    )
    probide_wait_stars_to_start_stars_purshase = provide(
        WaitStarsToStartStarsPurshase,
        scope=Scope.REQUEST,
    )
    provide_start_stars_purchase = provide(
        StartStarsPurchase,
        scope=Scope.REQUEST,
    )
    provide_start_stars_purchase_payment = provide(
        StartStarsPurchasePayment,
        scope=Scope.REQUEST,
    )


class ApplicationWithoutAiogramRequestDataProvider(Provider):
    provide_view_user = provide(ViewUser, scope=Scope.REQUEST)
    provide_register_user = provide(RegisterUser, scope=Scope.REQUEST)
    provide_remove_emoji = provide(RemoveEmoji, scope=Scope.REQUEST)
    probide_complete_stars_purshase_payment = provide(
        CompleteStarsPurshasePayment,
        scope=Scope.REQUEST,
    )
    probide_start_stars_purshase_payment_completion = provide(
        StartStarsPurshasePaymentCompletion,
        scope=Scope.REQUEST,
    )

    provide_wait_ai_type_to_start_game_with_ai = provide(
        WaitAiTypeToStartGameWithAi,
        scope=Scope.REQUEST,
    )
    provide_start_game_with_ai = provide(
        StartGameWithAi,
        scope=Scope.REQUEST,
    )
    provide_start_game = provide(StartGame, scope=Scope.REQUEST)
    provide_wait_game = provide(WaitGame, scope=Scope.REQUEST)
    provide_cancel_game = provide(CancelGame, scope=Scope.REQUEST)
    provide_make_move_in_game = provide(MakeMoveInGame, scope=Scope.REQUEST)
