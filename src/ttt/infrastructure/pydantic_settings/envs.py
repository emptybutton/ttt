from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class Envs(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TTT_")

    postgres_url: PostgresDsn
    redis_url: RedisDsn

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
