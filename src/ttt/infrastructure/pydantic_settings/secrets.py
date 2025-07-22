from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    YamlConfigSettingsSource,
)


class Secrets(BaseSettings):
    bot_token: str = Field(repr=False)
    payments_token: str = Field(repr=False)
    gemini_api_key: str = Field(repr=False)
    sentry_dsn: str = Field(repr=False)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        env_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        dotenv_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        file_secret_settings: PydanticBaseSettingsSource,  # noqa: ARG003
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (YamlConfigSettingsSource(settings_cls, "/run/secrets/secrets"),)

    @classmethod
    def load(cls) -> "Secrets":
        return Secrets()  # type: ignore[call-arg]
