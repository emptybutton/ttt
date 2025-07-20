from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
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

from ttt.application.common.ports.clock import Clock
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.randoms import Randoms
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.game.common.ports.game_ai_gateway import GameAiGateway
from ttt.application.game.common.ports.games import Games
from ttt.application.game.common.ports.waiting_locations import WaitingLocations
from ttt.application.game.game.ports.game_log import GameLog
from ttt.application.user.common.ports.paid_stars_purchase_payment_inbox import (  # noqa: E501
    PaidStarsPurchasePaymentInbox,
)
from ttt.application.user.common.ports.user_log import CommonUserLog
from ttt.application.user.common.ports.users import Users
from ttt.application.user.emoji_purchase.ports.user_log import (
    EmojiPurchaseUserLog,
)
from ttt.application.user.emoji_selection.ports.user_log import (
    EmojiSelectionUserLog,
)
from ttt.application.user.stars_purchase.ports.user_log import (
    StarsPurchaseUserLog,
)
from ttt.infrastructure.adapters.clock import NotMonotonicUtcClock
from ttt.infrastructure.adapters.game_ai_gateway import GeminiGameAiGateway
from ttt.infrastructure.adapters.game_log import StructlogGameLog
from ttt.infrastructure.adapters.games import InPostgresGames
from ttt.infrastructure.adapters.map import MapToPostgres
from ttt.infrastructure.adapters.paid_stars_purchase_payment_inbox import (
    InNatsPaidStarsPurchasePaymentInbox,
)
from ttt.infrastructure.adapters.randoms import MersenneTwisterRandoms
from ttt.infrastructure.adapters.transaction import InPostgresTransaction
from ttt.infrastructure.adapters.user_log import (
    StructlogCommonUserLog,
    StructlogEmojiPurchaseUserLog,
    StructlogEmojiSelectionUserLog,
    StructlogStarsPurchaseUserLog,
)
from ttt.infrastructure.adapters.users import InPostgresUsers
from ttt.infrastructure.adapters.uuids import UUIDv4s
from ttt.infrastructure.adapters.waiting_locations import (
    InRedisFixedBatchesWaitingLocations,
)
from ttt.infrastructure.background_tasks import BackgroundTasks
from ttt.infrastructure.nats.paid_stars_purchase_payment_inbox import (
    InNatsPaidStarsPurchasePaymentInbox as OriginalInNatsPaidStarsPurchasePaymentInbox,  # noqa: E501
)
from ttt.infrastructure.openai.gemini import Gemini, gemini
from ttt.infrastructure.pydantic_settings.envs import Envs
from ttt.infrastructure.pydantic_settings.secrets import Secrets
from ttt.infrastructure.redis.batches import InRedisFixedBatches
from ttt.infrastructure.structlog.logger import logger


class InfrastructureProvider(Provider):
    provide_envs = provide(source=Envs.load, scope=Scope.APP)
    provide_secrets = provide(source=Secrets.load, scope=Scope.APP)

    @provide(scope=Scope.APP)
    async def provide_background_tasks(self) -> AsyncIterator[BackgroundTasks]:
        async with BackgroundTasks() as tasks:
            yield tasks

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
            autobegin=False,
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

    @provide(scope=Scope.REQUEST)
    async def provide_request_redis(
        self,
        pool: ConnectionPool,
    ) -> AsyncIterator[Redis]:
        async with Redis(connection_pool=pool) as redis:
            yield redis

    @provide(scope=Scope.APP)
    async def provide_app_redis(self, envs: Envs) -> AsyncIterator[Redis]:
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
    async def provide_original_in_nats_paid_stars_purchase_payment_inbox(
        self, jetstream: JetStreamContext,
    ) -> AsyncIterator[OriginalInNatsPaidStarsPurchasePaymentInbox]:
        inbox = OriginalInNatsPaidStarsPurchasePaymentInbox(jetstream)
        async with inbox:
            yield inbox

    @provide(scope=Scope.APP)
    def provide_gemini(self, secrets: Secrets, envs: Envs) -> Gemini:
        return gemini(secrets.gemini_api_key, envs.gemini_url)

    @provide(scope=Scope.REQUEST)
    def provide_logger(self) -> FilteringBoundLogger:
        return logger()

    provide_in_nats_paid_stars_purchase_payment_inbox = provide(
        InNatsPaidStarsPurchasePaymentInbox,
        provides=PaidStarsPurchasePaymentInbox,
        scope=Scope.APP,
    )

    provide_transaction = provide(
        InPostgresTransaction,
        provides=Transaction,
        scope=Scope.REQUEST,
    )

    provide_games = provide(
        InPostgresGames,
        provides=Games,
        scope=Scope.REQUEST,
    )

    provide_users = provide(
        InPostgresUsers,
        provides=Users,
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

    @provide(scope=Scope.REQUEST)
    def provide_waiting_locations(
        self,
        redis: Redis,
        envs: Envs,
    ) -> WaitingLocations:
        return InRedisFixedBatchesWaitingLocations(
            InRedisFixedBatches(
                redis,
                "waiting_locations",
                envs.game_waiting_queue_pulling_timeout_min_ms,
                envs.game_waiting_queue_pulling_timeout_salt_ms,
            ),
        )

    provide_game_ai_gateway = provide(
        GeminiGameAiGateway,
        provides=GameAiGateway,
        scope=Scope.APP,
    )

    provide__game_log = provide(
        StructlogGameLog,
        provides=GameLog,
        scope=Scope.REQUEST,
    )

    provide_common_user_log = provide(
        StructlogCommonUserLog,
        provides=CommonUserLog,
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
        StructlogStarsPurchaseUserLog,
        provides=StarsPurchaseUserLog,
        scope=Scope.REQUEST,
    )
