from pydantic import NatsDsn, PositiveInt, PostgresDsn, RedisDsn
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class Envs(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TTT_")

    postgres_url: PostgresDsn
    postgres_echo: bool
    postgres_pool_size: int
    postgres_pool_timeout_seconds: int | float
    postgres_pool_recycle_seconds: int | float
    postgres_pool_pre_ping: bool

    redis_url: RedisDsn
    redis_pool_size: PositiveInt

    nats_url: NatsDsn

    game_waiting_queue_pulling_timeout_min_ms: int
    game_waiting_queue_pulling_timeout_salt_ms: int

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],  # noqa: ARG003
        init_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        file_secret_settings: PydanticBaseSettingsSource,  # noqa: ARG003
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            env_settings,
        )

    @classmethod
    def load(cls) -> "Envs":
        return Envs()  # type: ignore[call-arg]
