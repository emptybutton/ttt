from asyncio import Queue
from collections.abc import AsyncIterator
from typing import Annotated

from dishka import FromComponent, Provider, Scope, provide
from nats import connect as connect_to_nats
from nats.aio.client import Client as Nats
from nats.js import JetStreamContext
from redis.asyncio import ConnectionPool, Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from structlog.types import FilteringBoundLogger
from taskiq.receiver import Receiver

from ttt.application.common.errors.serialization_error import SerializationError
from ttt.application.common.ports.clock import Clock
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.randoms import Randoms
from ttt.application.common.ports.retry import Retry
from ttt.application.common.ports.transaction import (
    NotSerializableTransaction,
    ReadonlyTransaction,
    SerializableTransaction,
)
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.game.game.ports.game_ai_gateway import GameAiGateway
from ttt.application.game.game.ports.game_dao import GameDao
from ttt.application.game.game.ports.game_log import GameLog
from ttt.application.game.game.ports.game_tasks import GameTasks
from ttt.application.game.game.ports.games import Games
from ttt.application.invitation_to_game.game.ports.invitation_to_game_dao import (  # noqa: E501
    InvitationToGameDao,
)
from ttt.application.invitation_to_game.game.ports.invitation_to_game_log import (  # noqa: E501
    InvitationToGameLog,
)
from ttt.application.invitation_to_game.game.ports.invitations_to_game import (
    InvitationsToGame,
)
from ttt.application.stars_purchase.ports.stars_purchase_log import (
    StarsPurchaseLog,
)
from ttt.application.stars_purchase.ports.stars_purchase_tasks import (
    StarsPurchaseTasks,
)
from ttt.application.stars_purchase.ports.stars_purchases import StarsPurchases
from ttt.application.user.change_other_user_account.ports.user_log import (
    ChangeOtherUserAccountLog,
)
from ttt.application.user.common.ports.original_admin_token import (
    OriginalAdminToken,
)
from ttt.application.user.common.ports.user_locks import UserLocks
from ttt.application.user.common.ports.user_log import CommonUserLog
from ttt.application.user.common.ports.users import Users
from ttt.application.user.emoji_purchase.ports.user_log import (
    EmojiPurchaseUserLog,
)
from ttt.application.user.emoji_selection.ports.user_log import (
    EmojiSelectionUserLog,
)
from ttt.application.user.game.ports.user_log import GameUserLog
from ttt.infrastructure.adapters.clock import NotMonotonicUtcClock
from ttt.infrastructure.adapters.game_ai_gateway import GeminiGameAiGateway
from ttt.infrastructure.adapters.game_dao import PostgresGameDao
from ttt.infrastructure.adapters.game_log import StructlogGameLog
from ttt.infrastructure.adapters.game_tasks import NatsRemoteFuncGameTasks
from ttt.infrastructure.adapters.games import InPostgresGames
from ttt.infrastructure.adapters.invitation_to_game_dao import (
    PostgresInvitationToGameDao,
)
from ttt.infrastructure.adapters.invitation_to_game_log import (
    StructlogInvitationToGameLog,
)
from ttt.infrastructure.adapters.invitations_to_game import (
    InPostgresInvitationsToGame,
)
from ttt.infrastructure.adapters.map import MapToPostgres
from ttt.infrastructure.adapters.original_admin_token import (
    TokenAsOriginalAdminToken,
)
from ttt.infrastructure.adapters.randoms import MersenneTwisterRandoms
from ttt.infrastructure.adapters.retry import RetrierRetry
from ttt.infrastructure.adapters.stars_purchase_log import (
    StructlogStarsPurchaseLog,
)
from ttt.infrastructure.adapters.stars_purchase_tasks import (
    NatsRemoteFuncStarsPurchaseTasks,
)
from ttt.infrastructure.adapters.stars_purchases import PostgresStarsPurchases
from ttt.infrastructure.adapters.transaction import (
    InPostgresNotSerializableTransaction,
    InPostgresReadonlyTransaction,
    InPostgresSerializableTransaction,
)
from ttt.infrastructure.adapters.user_locks import InPostgresUserLocks
from ttt.infrastructure.adapters.user_log import (
    StructlogChangeOtherUserAccountLog,
    StructlogCommonUserLog,
    StructlogEmojiPurchaseUserLog,
    StructlogEmojiSelectionUserLog,
    StructlogGameUserLog,
)
from ttt.infrastructure.adapters.users import InPostgresUsers
from ttt.infrastructure.adapters.uuids import UUIDv4s
from ttt.infrastructure.multi_asynccontextmanager import (
    multi_asynccontextmanager,
)
from ttt.infrastructure.openai.gemini import Gemini, gemini
from ttt.infrastructure.processors.auto_cancel_invitations_to_game_processor import (  # noqa: E501
    AutoCancelInvitationsToGameProcessor,
)
from ttt.infrastructure.processors.matchmake_processor import MatchmakeProcessor
from ttt.infrastructure.processors.processor import Processor
from ttt.infrastructure.pydantic_settings.envs import Envs
from ttt.infrastructure.pydantic_settings.secrets import Secrets
from ttt.infrastructure.remote_funcs.complete_stars_purchase_payment import (
    complete_stars_purchase_payment_remotely,
)
from ttt.infrastructure.remote_funcs.make_ai_move_in_game import (
    make_ai_move_in_game_remotely,
)
from ttt.infrastructure.retrier import Retrier


class InfrastructureProvider(Provider):
    provide_envs = provide(source=Envs.load, scope=Scope.APP)
    provide_secrets = provide(source=Secrets.load, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def provide_original_admin_token(
        self, secrets: Secrets,
    ) -> OriginalAdminToken:
        return TokenAsOriginalAdminToken(secrets.admin_token)

    @provide(scope=Scope.APP)
    async def provide_postgres_engine(self, envs: Envs) -> AsyncEngine:
        return create_async_engine(
            str(envs.postgres_url),
            echo=envs.postgres_echo,
            max_overflow=0,
            pool_size=envs.postgres_pool_size,
            pool_timeout=envs.postgres_pool_timeout_seconds,
            pool_recycle=envs.postgres_pool_recycle_seconds,
            pool_pre_ping=envs.postgres_pool_pre_ping,
        )

    @provide(scope=Scope.REQUEST)
    async def provide_postgres_session(
        self,
        engine: AsyncEngine,
    ) -> AsyncIterator[AsyncSession]:
        session = AsyncSession(
            engine,
            autoflush=False,
            expire_on_commit=False,
        )

        async with session:
            yield session

    @provide(scope=Scope.APP)
    async def provide_redis_pool(
        self,
        envs: Envs,
    ) -> AsyncIterator[ConnectionPool]:
        pool = ConnectionPool.from_url(
            str(envs.redis_url),
            max_connections=envs.redis_pool_size,
        )
        try:
            yield pool
        finally:
            await pool.aclose()

    @provide(scope=Scope.APP)
    async def provide_redis(self, envs: Envs) -> AsyncIterator[Redis]:
        async with Redis.from_url(str(envs.redis_url)) as redis:
            yield redis

    @provide(scope=Scope.APP)
    async def provide_nats(
        self,
        envs: Envs,
    ) -> AsyncIterator[Nats]:
        nats = await connect_to_nats(str(envs.nats_url))

        async with nats:
            yield nats

    @provide(scope=Scope.APP)
    async def provide_jetstream(self, nats: Nats) -> JetStreamContext:
        return nats.jetstream()

    @provide(scope=Scope.APP)
    def provide_gemini(self, secrets: Secrets, envs: Envs) -> Gemini:
        return gemini(secrets.gemini_api_key, envs.gemini_url)

    provide_serializable_transaction = provide(
        InPostgresSerializableTransaction,
        provides=SerializableTransaction,
        scope=Scope.REQUEST,
    )
    provide_not_serializable_transaction = provide(
        InPostgresNotSerializableTransaction,
        provides=NotSerializableTransaction,
        scope=Scope.REQUEST,
    )
    provide_readonly_transaction = provide(
        InPostgresReadonlyTransaction,
        provides=ReadonlyTransaction,
        scope=Scope.REQUEST,
    )

    provide_games = provide(
        InPostgresGames,
        provides=Games,
        scope=Scope.REQUEST,
    )

    @provide(scope=Scope.REQUEST)
    def provide_users(
        self,
        session: AsyncSession,
        envs: Envs,
    ) -> Users:
        return InPostgresUsers(
            session,
            _users_to_matchmake_limit=envs.matchmaking_worker_max_users,
        )

    provide_stars_purchases = provide(
        PostgresStarsPurchases,
        provides=StarsPurchases,
        scope=Scope.REQUEST,
    )

    provide_invitations_to_game = provide(
        InPostgresInvitationsToGame,
        provides=InvitationsToGame,
        scope=Scope.REQUEST,
    )

    provide_invitation_to_game_dao = provide(
        PostgresInvitationToGameDao,
        provides=InvitationToGameDao,
        scope=Scope.REQUEST,
    )

    provide_game_dao = provide(
        PostgresGameDao,
        provides=GameDao,
        scope=Scope.REQUEST,
    )

    provide_map = provide(
        MapToPostgres,
        provides=Map,
        scope=Scope.REQUEST,
    )

    provide_uuids = provide(
        UUIDv4s,
        provides=UUIDs,
        scope=Scope.APP,
    )

    provide_clock = provide(
        NotMonotonicUtcClock,
        provides=Clock,
        scope=Scope.APP,
    )

    @provide(scope=Scope.APP)
    def provide_randoms(self) -> Randoms:
        return MersenneTwisterRandoms()

    provide_game_ai_gateway = provide(
        GeminiGameAiGateway,
        provides=GameAiGateway,
        scope=Scope.APP,
    )

    provide_game_log = provide(
        StructlogGameLog,
        provides=GameLog,
        scope=Scope.REQUEST,
    )

    provide_common_user_log = provide(
        StructlogCommonUserLog,
        provides=CommonUserLog,
        scope=Scope.REQUEST,
    )

    provide_game_user_log = provide(
        StructlogGameUserLog,
        provides=GameUserLog,
        scope=Scope.REQUEST,
    )

    provide_emoji_purchase_user_log = provide(
        StructlogEmojiPurchaseUserLog,
        provides=EmojiPurchaseUserLog,
        scope=Scope.REQUEST,
    )

    provide_emoji_selection_user_log = provide(
        StructlogEmojiSelectionUserLog,
        provides=EmojiSelectionUserLog,
        scope=Scope.REQUEST,
    )

    provide_stars_purchase_user_log = provide(
        StructlogStarsPurchaseLog,
        provides=StarsPurchaseLog,
        scope=Scope.REQUEST,
    )

    provide_change_other_user_account_log = provide(
        StructlogChangeOtherUserAccountLog,
        provides=ChangeOtherUserAccountLog,
        scope=Scope.REQUEST,
    )

    provide_invitation_to_game_log = provide(
        StructlogInvitationToGameLog,
        provides=InvitationToGameLog,
        scope=Scope.REQUEST,
    )
    provide_user_locks = provide(
        InPostgresUserLocks,
        provides=UserLocks,
        scope=Scope.REQUEST,
    )

    provide_game_tasks = provide(
        NatsRemoteFuncGameTasks,
        provides=GameTasks,
        scope=Scope.APP,
    )
    provide_stars_purchase_tasks = provide(
        NatsRemoteFuncStarsPurchaseTasks,
        provides=StarsPurchaseTasks,
        scope=Scope.APP,
    )

    @provide(scope=Scope.REQUEST)
    def provide_retrier(self, envs: Envs) -> Retrier:
        return Retrier(_max_retries_map={
            SerializationError: envs.serialization_error_max_retries,
        })

    provide_retry = provide(RetrierRetry, provides=Retry, scope=Scope.REQUEST)

    @provide(scope=Scope.APP)
    def provide_auto_cancel_invitations_to_game_task(
        self,
        envs: Envs,
        logger: Annotated[FilteringBoundLogger, FromComponent("app")],
    ) -> AutoCancelInvitationsToGameProcessor:
        return AutoCancelInvitationsToGameProcessor(
            _interval_seconds=(
                envs.auto_cancel_invitations_to_game_interval_seconds
            ),
            _logger=logger,
        )

    @provide(scope=Scope.APP)
    def provide_matchmake_processor(
        self,
        envs: Envs,
        logger: Annotated[FilteringBoundLogger, FromComponent("app")],
    ) -> MatchmakeProcessor:
        return MatchmakeProcessor(
            _max_workers=envs.matchmaking_max_workers,
            _worker_creation_interval_seconds=(
                envs.matchmaking_worker_creation_interval_seconds
            ),
            _logger=logger,
        )

    @provide(scope=Scope.APP)
    async def processors(
        self,
        js: JetStreamContext,
        auto_cancel_invitations_to_game_processor: (
            AutoCancelInvitationsToGameProcessor
        ),
        matchmake_processor: MatchmakeProcessor,
    ) -> AsyncIterator[tuple[Processor, ...]]:
        nats_remote_funcs = (
            make_ai_move_in_game_remotely,
            complete_stars_purchase_payment_remotely,
        )
        multi_startup = multi_asynccontextmanager(*(
            func.startup(js) for func in nats_remote_funcs
        ))
        async with multi_startup:
            nats_remote_func_processors = (
                func.processor
                for func in nats_remote_funcs
            )
            yield (
                auto_cancel_invitations_to_game_processor,
                matchmake_processor,
                *nats_remote_func_processors,
            )
