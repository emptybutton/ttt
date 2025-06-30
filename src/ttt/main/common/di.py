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

from ttt.application.common.ports.clock import Clock
from ttt.application.common.ports.map import Map
from ttt.application.common.ports.randoms import Randoms
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.game.ports.games import Games
from ttt.application.game.ports.waiting_locations import WaitingLocations
from ttt.application.player.ports.players import Players
from ttt.infrastructure.adapters.clock import NotMonotonicUtcClock
from ttt.infrastructure.adapters.games import InPostgresGames
from ttt.infrastructure.adapters.map import MapToPostgres
from ttt.infrastructure.adapters.players import InPostgresPlayers
from ttt.infrastructure.adapters.randoms import MersenneTwisterRandoms
from ttt.infrastructure.adapters.transaction import InPostgresTransaction
from ttt.infrastructure.adapters.uuids import UUIDv4s
from ttt.infrastructure.adapters.waiting_locations import (
    InRedisFixedBatchesWaitingLocations,
)
from ttt.infrastructure.background_tasks import BackgroundTasks
from ttt.infrastructure.nats.paid_stars_purchase_payment_inbox import (
    InNatsPaidStarsPurchasePaymentInbox,
)
from ttt.infrastructure.pydantic_settings.envs import Envs
from ttt.infrastructure.pydantic_settings.secrets import Secrets
from ttt.infrastructure.redis.batches import InRedisFixedBatches


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
    async def provide_in_nats_paid_stars_purchase_payment_inbox(
        self, jetstream: JetStreamContext,
    ) -> AsyncIterator[InNatsPaidStarsPurchasePaymentInbox]:
        async with InNatsPaidStarsPurchasePaymentInbox(jetstream) as inbox:
            yield inbox

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

    provide_players = provide(
        InPostgresPlayers,
        provides=Players,
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
