from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Annotated, cast

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import BaseStorage, DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import (
    CallbackQuery,
    Message,
    PreCheckoutQuery,
    TelegramObject,
)
from aiogram_dialog import BgManagerFactory, setup_dialogs
from aiogram_dialog.manager.bg_manager import BgManagerFactoryImpl
from aiogram_dialog.manager.manager import ManagerImpl
from dishka import (
    FromComponent,
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
from ttt.application.game.game.make_ai_move_in_game import MakeAiMoveInGame
from ttt.application.game.game.make_move_in_game import MakeMoveInGame
from ttt.application.game.game.ports.game_views import GameViews
from ttt.application.game.game.start_game_with_ai import StartGameWithAi
from ttt.application.game.game.view_game import ViewGame
from ttt.application.invitation_to_game.game.accpet_invitation_to_game import (
    AcceptInvitationToGame,
)
from ttt.application.invitation_to_game.game.auto_cancel_invitations_to_game import (  # noqa: E501
    AutoCancelInvitationsToGame,
)
from ttt.application.invitation_to_game.game.cancel_invitation_to_game import (
    CancelInvitationToGame,
)
from ttt.application.invitation_to_game.game.invite_to_game import InviteToGame
from ttt.application.invitation_to_game.game.ports.invitation_to_game_views import (  # noqa: E501
    InvitationToGameViews,
)
from ttt.application.invitation_to_game.game.reject_invitation_to_game import (
    RejectInvitationToGame,
)
from ttt.application.invitation_to_game.game.view_incoming_invitation_to_game import (  # noqa: E501
    ViewIncomingInvitationToGame,
)
from ttt.application.invitation_to_game.game.view_incoming_invitations_to_game import (  # noqa: E501
    ViewIncomingInvitationsToGame,
)
from ttt.application.invitation_to_game.game.view_one_incoming_invitation_to_game import (  # noqa: E501
    ViewOneIncomingInvitationToGame,
)
from ttt.application.invitation_to_game.game.view_outcoming_invitations_to_game import (  # noqa: E501
    ViewOutcomingInvitationsToGame,
)
from ttt.application.stars_purchase.complete_stars_purchase_payment import (
    CompleteStarsPurchasePayment,
)
from ttt.application.stars_purchase.ports.stars_purchase_payment_gateway import (  # noqa: E501
    StarsPurchasePaymentGateway,
)
from ttt.application.stars_purchase.ports.stars_purchase_views import (
    StarsPurchaseViews,
)
from ttt.application.stars_purchase.start_stars_purchase import (
    StartStarsPurchase,
)
from ttt.application.stars_purchase.start_stars_purchase_payment import (
    StartStarsPurchasePayment,
)
from ttt.application.stars_purchase.start_stars_purchase_payment_completion import (  # noqa: E501
    StartStarsPurchasePaymentCompletion,
)
from ttt.application.user.authorize_as_admin import AuthorizeAsAdmin
from ttt.application.user.authorize_other_user_as_admin import (
    AuthorizeOtherUserAsAdmin,
)
from ttt.application.user.change_other_user_account.change_other_user_account import (  # noqa: E501
    ChangeOtherUserAccount,
)
from ttt.application.user.change_other_user_account.ports.user_views import (
    ChangeOtherUserAccountViews,
)
from ttt.application.user.change_other_user_account.set_other_user_account import (  # noqa: E501
    SetOtherUserAccount,
)
from ttt.application.user.change_other_user_account.view_user_account_to_change import (  # noqa: E501
    ViewUserAccountToChange,
)
from ttt.application.user.common.ports.user_views import CommonUserViews
from ttt.application.user.deauthorize_other_user_as_admin import (
    DeauthorizeOtherUserAsAdmin,
)
from ttt.application.user.emoji_purchase.buy_emoji import BuyEmoji
from ttt.application.user.emoji_purchase.ports.user_views import (
    EmojiPurchaseUserViews,
)
from ttt.application.user.emoji_selection.ports.user_views import (
    EmojiSelectionUserViews,
)
from ttt.application.user.emoji_selection.select_emoji import SelectEmoji
from ttt.application.user.game.dont_wait_for_matchmaking import (
    DontWaitForMatchmaking,
)
from ttt.application.user.game.matchmake import Matchmake
from ttt.application.user.game.ports.user_views import GameUserViews
from ttt.application.user.game.view_matchmaking import ViewMatchmaking
from ttt.application.user.game.wait_for_matchmaking import WaitForMatchmaking
from ttt.application.user.register_user import RegisterUser
from ttt.application.user.relinquish_admin_right import RelinquishAdminRight
from ttt.application.user.view_admin_menu import ViewAdminMenu
from ttt.application.user.view_main_menu import ViewMainMenu
from ttt.application.user.view_other_user import ViewOtherUser
from ttt.application.user.view_user import ViewUser
from ttt.application.user.view_user_emojis import ViewUserEmojis
from ttt.infrastructure.pydantic_settings.envs import Envs
from ttt.infrastructure.pydantic_settings.secrets import Secrets
from ttt.presentation.adapters.emojis import PictographsAsEmojis
from ttt.presentation.adapters.game_views import (
    AiogramGameViews,
)
from ttt.presentation.adapters.invitation_to_game_views import (
    AiogramInvitationToGameViews,
)
from ttt.presentation.adapters.stars_purchase_payment_gateway import (
    AiogramPaymentGateway,
)
from ttt.presentation.adapters.stars_purchase_views import (
    AiogramStarsPurchaseViews,
)
from ttt.presentation.adapters.user_views import (
    AiogramChangeOtherUserAccountViews,
    AiogramCommonUserViews,
    AiogramEmojiPurchaseUserViews,
    AiogramEmojiSelectionUserViews,
    AiogramGameUserViews,
)
from ttt.presentation.aiogram.common.bots import ttt_bot
from ttt.presentation.aiogram.common.routes.all import common_routers
from ttt.presentation.aiogram.user.routes.all import user_routers
from ttt.presentation.aiogram_dialog.admin_dialog import admin_dialog
from ttt.presentation.aiogram_dialog.common.dialog_manager_for_user import (
    DialogManagerForUser,
)
from ttt.presentation.aiogram_dialog.main_dialog import main_dialog
from ttt.presentation.result_buffer import ResultBuffer
from ttt.presentation.tasks.auto_cancel_invitations_to_game_task import (
    AutoCancelInvitationsToGameTask,
)
from ttt.presentation.tasks.matchmake_tasks import MatchmakeTasks
from ttt.presentation.tasks.unkillable_tasks import UnkillableTasks
from ttt.presentation.unkillable_task_group import UnkillableTaskGroup


@dataclass
class NoMessageInEventError(Exception):
    event: TelegramObject | None


class PresentationProvider(Provider):
    provide_aiogram_middleware_data = from_context(
        AiogramMiddlewareData | None,
        scope=Scope.REQUEST,
    )
    provide_event = from_context(TelegramObject | None, scope=Scope.REQUEST)

    @provide(scope=Scope.APP)
    def provide_strage(self, redis: Redis) -> BaseStorage:
        return RedisStorage(redis, DefaultKeyBuilder(with_destiny=True))

    @provide(scope=Scope.APP)
    def provide_bg_manager_factory(self, dp: Dispatcher) -> BgManagerFactory:
        return BgManagerFactoryImpl(dp)

    @provide(scope=Scope.REQUEST)
    def provide_manager_impl(
        self, middleware_data: AiogramMiddlewareData | None,
    ) -> ManagerImpl | None:
        if middleware_data is None:
            return None

        return cast(ManagerImpl, middleware_data.get("dialog_manager"))

    @provide(scope=Scope.APP)
    async def provide_bot(self, secrets: Secrets) -> AsyncIterator[Bot]:
        bot = Bot(secrets.bot_token)

        async with bot:
            await ttt_bot(bot)
            yield bot

    provide_dialog_manager_for_user = provide(
        DialogManagerForUser, scope=Scope.REQUEST,
    )

    provide_emoji = provide(
        PictographsAsEmojis,
        provides=Emojis,
        scope=Scope.REQUEST,
    )

    provide_game_views = provide(
        AiogramGameViews,
        provides=GameViews,
        scope=Scope.REQUEST,
    )

    provide_user_views = provide(
        AiogramCommonUserViews,
        provides=CommonUserViews,
        scope=Scope.REQUEST,
    )
    provide_game_user_views = provide(
        AiogramGameUserViews,
        provides=GameUserViews,
        scope=Scope.REQUEST,
    )
    provide_stars_purchase_user_views = provide(
        AiogramStarsPurchaseViews,
        provides=StarsPurchaseViews,
        scope=Scope.REQUEST,
    )
    provide_emoji_selection_user_views = provide(
        AiogramEmojiSelectionUserViews,
        provides=EmojiSelectionUserViews,
        scope=Scope.REQUEST,
    )
    provide_emoji_purchase_user_views = provide(
        AiogramEmojiPurchaseUserViews,
        provides=EmojiPurchaseUserViews,
        scope=Scope.REQUEST,
    )
    provide_change_other_user_account_views = provide(
        AiogramChangeOtherUserAccountViews,
        provides=ChangeOtherUserAccountViews,
        scope=Scope.REQUEST,
    )

    provide_invitation_to_game_views = provide(
        AiogramInvitationToGameViews,
        provides=InvitationToGameViews,
        scope=Scope.REQUEST,
    )

    @provide(scope=Scope.REQUEST)
    def provide_result_buffer(self) -> ResultBuffer:
        return ResultBuffer()

    @provide(scope=Scope.APP)
    def provide_auto_cancel_invitations_to_game_task(
        self, envs: Envs,
    ) -> AutoCancelInvitationsToGameTask:
        return AutoCancelInvitationsToGameTask(
            _interval_seconds=(
                envs.auto_cancel_invitations_to_game_interval_seconds
            ),
        )

    @provide(scope=Scope.APP)
    def provide_matchmake_tasks(
        self,
        envs: Envs,
        logger: Annotated[FilteringBoundLogger, FromComponent("app")],
    ) -> MatchmakeTasks:
        return MatchmakeTasks(
            _max_workers=envs.matchmaking_max_workers,
            _worker_creation_interval_seconds=(
                envs.matchmaking_worker_creation_interval_seconds
            ),
            _logger=logger,
        )

    @provide(scope=Scope.APP)
    async def unkillable_task_group(
        self, logger: Annotated[FilteringBoundLogger, FromComponent("app")],
    ) -> AsyncIterator[UnkillableTaskGroup]:
        async with UnkillableTaskGroup(logger) as group:
            yield group

    @provide(scope=Scope.APP)
    async def unkillable_tasks(
        self,
        task_group: UnkillableTaskGroup,
        auto_cancel_invitations_to_game_task: AutoCancelInvitationsToGameTask,
        matchmake_tasks: MatchmakeTasks,
    ) -> UnkillableTasks:
        tasks = (
            auto_cancel_invitations_to_game_task,
            matchmake_tasks,
        )
        return UnkillableTasks(tasks, task_group)

    @provide(scope=Scope.APP)
    def provide_dp(self, storage: BaseStorage) -> Dispatcher:
        dp = Dispatcher(name="main", storage=storage)

        dp.include_routers(
            *common_routers,
            *user_routers,
        )
        dp.include_routers(main_dialog, admin_dialog)

        setup_dialogs(dp)

        return dp

    @provide(scope=Scope.REQUEST)
    def provide_message(self, event: TelegramObject | None) -> Message:
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
        event: TelegramObject | None,
    ) -> PreCheckoutQuery | None:
        match event:
            case PreCheckoutQuery():
                return event
            case _:
                return None

    @provide(scope=Scope.REQUEST)
    def provide_callback_query(
        self,
        event: TelegramObject | None,
    ) -> CallbackQuery | None:
        match event:
            case CallbackQuery():
                return event
            case _:
                return None

    @provide(scope=Scope.REQUEST)
    def provide_stars_purchase_payment_gateway(
        self,
        pre_checkout_query: PreCheckoutQuery | None,
        secrets: Secrets,
        bot: Bot,
        dialog_manager_for_user: DialogManagerForUser,
    ) -> StarsPurchasePaymentGateway:
        return AiogramPaymentGateway(
            pre_checkout_query,
            bot,
            secrets.payments_token,
            dialog_manager_for_user,
        )


class ApplicationProvider(Provider):
    provide_buy_emoji = provide(BuyEmoji, scope=Scope.REQUEST)
    provide_select_emoji = provide(SelectEmoji, scope=Scope.REQUEST)
    provide_view_user_emojis = provide(
        ViewUserEmojis,
        scope=Scope.REQUEST,
    )
    provide_view_main_menu = provide(
        ViewMainMenu,
        scope=Scope.REQUEST,
    )
    provide_view_user = provide(ViewUser, scope=Scope.REQUEST)
    provide_register_user = provide(RegisterUser, scope=Scope.REQUEST)
    provide_authorize_as_admin = provide(AuthorizeAsAdmin, scope=Scope.REQUEST)
    provide_relinquish_admin_right = provide(
        RelinquishAdminRight,
        scope=Scope.REQUEST,
    )
    provide_view_admin_menu = provide(ViewAdminMenu, scope=Scope.REQUEST)
    provide_view_other_user = provide(ViewOtherUser, scope=Scope.REQUEST)
    provide_authorize_other_user_as_admin = provide(
        AuthorizeOtherUserAsAdmin, scope=Scope.REQUEST,
    )
    provide_deauthorize_other_user_as_admin = provide(
        DeauthorizeOtherUserAsAdmin, scope=Scope.REQUEST,
    )
    provide_set_other_user_account = provide(
        SetOtherUserAccount, scope=Scope.REQUEST,
    )
    provide_change_other_user_account = provide(
        ChangeOtherUserAccount, scope=Scope.REQUEST,
    )
    provide_view_user_account_to_change = provide(
        ViewUserAccountToChange, scope=Scope.REQUEST,
    )
    provide_matchmake = provide(Matchmake, scope=Scope.REQUEST)
    provide_wait_for_matchmaking = provide(
        WaitForMatchmaking, scope=Scope.REQUEST,
    )
    provide_dont_wait_for_matchmaking = provide(
        DontWaitForMatchmaking, scope=Scope.REQUEST,
    )
    provide_view_matchmaking = provide(ViewMatchmaking, scope=Scope.REQUEST)

    provide_start_stars_purchase = provide(
        StartStarsPurchase,
        scope=Scope.REQUEST,
    )
    provide_start_stars_purchase_payment = provide(
        StartStarsPurchasePayment,
        scope=Scope.REQUEST,
    )
    probide_complete_stars_purchase_payment = provide(
        CompleteStarsPurchasePayment,
        scope=Scope.REQUEST,
    )
    probide_start_stars_purchase_payment_completion = provide(
        StartStarsPurchasePaymentCompletion,
        scope=Scope.REQUEST,
    )

    provide_start_game_with_ai = provide(
        StartGameWithAi,
        scope=Scope.REQUEST,
    )
    provide_cancel_game = provide(CancelGame, scope=Scope.REQUEST)
    provide_make_move_in_game = provide(MakeMoveInGame, scope=Scope.REQUEST)
    provide_make_ai_move_in_game = provide(
        MakeAiMoveInGame, scope=Scope.REQUEST,
    )
    provide_view_game = provide(ViewGame, scope=Scope.REQUEST)

    provide_accept_invitation_to_game = provide(
        AcceptInvitationToGame, scope=Scope.REQUEST,
    )
    provide_cancel_invitation_to_game = provide(
        CancelInvitationToGame, scope=Scope.REQUEST,
    )
    provide_auto_cancel_invitations_to_game = provide(
        AutoCancelInvitationsToGame, scope=Scope.REQUEST,
    )
    provide_invite_to_game = provide(
        InviteToGame, scope=Scope.REQUEST,
    )
    provide_reject_invitation_to_game = provide(
        RejectInvitationToGame, scope=Scope.REQUEST,
    )
    provide_view_outcoming_invitations_to_game = provide(
        ViewOutcomingInvitationsToGame, scope=Scope.REQUEST,
    )
    provide_view_incoming_invitations_to_game = provide(
        ViewIncomingInvitationsToGame, scope=Scope.REQUEST,
    )
    provide_view_incoming_invitation_to_game = provide(
        ViewIncomingInvitationToGame, scope=Scope.REQUEST,
    )
    provide_view_one_incoming_invitation_to_game = provide(
        ViewOneIncomingInvitationToGame, scope=Scope.REQUEST,
    )
