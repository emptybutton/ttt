from collections.abc import AsyncIterator

from aiogram.methods import SendMessage
from dishka import Provider, Scope, provide
from redis.asyncio import ConnectionPool, Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)

from ttt.application.common.ports.map import Map
from ttt.application.common.ports.player_message_sending import (
    PlayerMessageSending,
)
from ttt.application.common.ports.players import Players
from ttt.application.common.ports.transaction import Transaction
from ttt.application.common.ports.uuids import UUIDs
from ttt.application.game.ports.games import Games
from ttt.application.game.ports.waiting_locations import WaitingLocations
from ttt.application.player.ports.player_views import PlayerViews
from ttt.application.player.register_player import RegisterPlayer
from ttt.application.player.view_player import ViewPlayer
from ttt.infrastructure.adapters.games import InPostgresGames
from ttt.infrastructure.adapters.map import MapToPostgres
from ttt.infrastructure.adapters.players import InPostgresPlayers
from ttt.infrastructure.adapters.transaction import in_postgres_transaction
from ttt.infrastructure.adapters.uuids import UUIDv4s
from ttt.infrastructure.adapters.waiting_locations import (
    InRedisFixedBatchesWaitingLocations,
)
from ttt.infrastructure.background_tasks import BackgroundTasks
from ttt.infrastructure.pydantic_settings.envs import Envs
from ttt.infrastructure.pydantic_settings.secrets import Secrets
from ttt.infrastructure.redis.batches import InRedisFixedBatches
from ttt.presentation.adapters.player_message_sending import (
    AiogramPlayerMessageSending,
)
from ttt.presentation.adapters.player_views import (
    AiogramMessagesFromPostgresAsPlayerViews,
)
from ttt.presentation.unkillable_tasks import UnkillableTasks


class CommonProvider(Provider):
    provide_envs = provide(source=Envs.load, scope=Scope.APP)
    provide_secrets = provide(source=Secrets.load, scope=Scope.APP)

    @provide(scope=Scope.APP)
    async def provide_background_tasks(self) -> AsyncIterator[BackgroundTasks]:
        async with BackgroundTasks() as tasks:
            yield tasks

    @provide(scope=Scope.APP)
    async def provide_unkillable_tasks(self) -> AsyncIterator[UnkillableTasks]:
        async with UnkillableTasks() as tasks:
            yield tasks

    @provide(scope=Scope.APP)
    async def provide_postgres_engine(self, envs: Envs) -> AsyncEngine:
        return create_async_engine(str(envs.postgres_url))

    @provide(scope=Scope.REQUEST)
    async def provide_postgres_session(
        self, engine: AsyncEngine,
    ) -> AsyncIterator[AsyncSession]:
        session = AsyncSession(
            engine,
            autoflush=False,
            autobegin=False,
            expire_on_commit=True,
        )

        async with session:
            yield session

    @provide(scope=Scope.APP)
    async def provide_redis_pool(
        self, envs: Envs,
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
    async def provide_redis(
        self, pool: ConnectionPool,
    ) -> AsyncIterator[Redis]:
        async with Redis(connection_pool=pool) as redis:
            yield redis

    @provide(scope=Scope.REQUEST)
    def provide_transaction(
        self, session: AsyncSession,
    ) -> Transaction:
        return in_postgres_transaction(session=session)

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

    @provide(scope=Scope.REQUEST)
    def provide_waiting_locations(
        self, redis: Redis, envs: Envs,
    ) -> WaitingLocations:
        return InRedisFixedBatchesWaitingLocations(InRedisFixedBatches(
            redis,
            "waiting_locations",
            envs.game_waiting_queue_pulling_timeout_min_ms,
            envs.game_waiting_queue_pulling_timeout_salt_ms,
        ))

    provide_player_views = provide(
        AiogramMessagesFromPostgresAsPlayerViews,
        provides=PlayerViews[SendMessage],
        scope=Scope.REQUEST,
    )

    provide_player_message_sending = provide(
        AiogramPlayerMessageSending,
        provides=PlayerMessageSending,
        scope=Scope.REQUEST,
    )

    provide_register_player = provide(RegisterPlayer, scope=Scope.REQUEST)

    provide_view_player = provide(
        ViewPlayer[SendMessage], scope=Scope.REQUEST,
    )
