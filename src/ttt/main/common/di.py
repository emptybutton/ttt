from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
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
from ttt.application.game.cancel_game import CancelGame
from ttt.application.game.make_move_in_game import MakeMoveInGame
from ttt.application.game.ports.games import Games
from ttt.application.game.ports.waiting_locations import WaitingLocations
from ttt.application.game.start_game import StartGame
from ttt.application.game.wait_game import WaitGame
from ttt.application.player.buy_emoji import BuyEmoji
from ttt.application.player.ports.players import Players
from ttt.application.player.register_player import RegisterPlayer
from ttt.application.player.remove_emoji import RemoveEmoji
from ttt.application.player.select_emoji import SelectEmoji
from ttt.application.player.view_player import ViewPlayer
from ttt.application.player.wait_emoji_to_buy import WaitEmojiToBuy
from ttt.application.player.wait_emoji_to_select import WaitEmojiToSelect
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
from ttt.infrastructure.pydantic_settings.envs import Envs
from ttt.infrastructure.pydantic_settings.secrets import Secrets
from ttt.infrastructure.redis.batches import InRedisFixedBatches


class CommonProvider(Provider):
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

    provide_view_player = provide(ViewPlayer, scope=Scope.REQUEST)
    provide_register_player = provide(RegisterPlayer, scope=Scope.REQUEST)
    provide_buy_emoji = provide(BuyEmoji, scope=Scope.REQUEST)
    provide_wait_emoji_to_buy = provide(WaitEmojiToBuy, scope=Scope.REQUEST)
    provide_select_emoji = provide(SelectEmoji, scope=Scope.REQUEST)
    provide_wait_emoji_to_select = provide(
        WaitEmojiToSelect, scope=Scope.REQUEST,
    )
    provide_remove_emoji = provide(RemoveEmoji, scope=Scope.REQUEST)

    provide_start_game = provide(StartGame, scope=Scope.REQUEST)
    provide_wait_game = provide(WaitGame, scope=Scope.REQUEST)
    provide_cancel_game = provide(CancelGame, scope=Scope.REQUEST)
    provide_make_move_in_game = provide(MakeMoveInGame, scope=Scope.REQUEST)
