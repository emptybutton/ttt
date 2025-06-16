type JWT = str

from pydantic_settings import BaseSettings, SettingsConfigDict  # noqa: E402


class Settings(BaseSettings):
    model_config = SettingsConfigDict(secrets_dir='/var/run')

    database_password: str
